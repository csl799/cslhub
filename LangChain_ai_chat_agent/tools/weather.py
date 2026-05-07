import json
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import date, datetime, time, timedelta
from typing import Any, Optional
from zoneinfo import ZoneInfo

from langchain.tools import tool

_USER_AGENT = "LangChainWeatherTool/1.0 (+local)"


def _http_get_json(url: str) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def _resolve_coordinates(location: str) -> tuple[float, float, str]:
    loc = location.strip()
    parts = [p.strip() for p in loc.replace("，", ",").split(",") if p.strip()]
    if len(parts) == 2:
        try:
            lat, lon = float(parts[0]), float(parts[1])
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return lat, lon, f"{lat},{lon}"
        except ValueError:
            pass
    q = urllib.parse.quote(loc)
    data = _http_get_json(
        f"https://geocoding-api.open-meteo.com/v1/search?name={q}&count=1&language=zh"
    )
    results = data.get("results") or []
    if not results:
        raise ValueError(f"无法解析地点：{location!r}")
    r = results[0]
    return float(r["latitude"]), float(r["longitude"]), r.get("name", loc)


_WMO_WEATHER = {
    0: "晴天",
    1: "大部晴朗",
    2: "局部多云",
    3: "阴天",
    45: "雾",
    48: "沉积霜雾",
    51: "小毛毛雨",
    53: "中毛毛雨",
    55: "强毛毛雨",
    61: "小雨",
    63: "中雨",
    65: "大雨",
    71: "小雪",
    73: "中雪",
    75: "大雪",
    80: "阵雨",
    81: "强阵雨",
    82: "暴雨阵雨",
    95: "雷暴",
    96: "雷暴伴冰雹",
    99: "强雷暴伴冰雹",
}


def _weather_label(code: Optional[float]) -> str:
    if code is None:
        return "未知"
    key = int(round(code))
    return _WMO_WEATHER.get(key, f"代码{key}")


def _parse_anchor_date(anchor_date: Optional[str], tz: ZoneInfo) -> date:
    if anchor_date and anchor_date.strip():
        raw = anchor_date.strip()[:10]
        try:
            return datetime.strptime(raw, "%Y-%m-%d").date()
        except ValueError as e:
            raise ValueError(f"anchor_date 须为 YYYY-MM-DD：{raw!r}") from e
    return datetime.now(tz).date()


@tool
def get_weather(
    location: str,
    start_offset_days: int = 0,
    num_days: int = 1,
    anchor_date: Optional[str] = None,
) -> str:
    """
    使用 Open-Meteo 查询指定地点在一段连续自然日内的预报（实时接口数据）。

    时间由「锚定日 + 偏移 + 天数」决定，均在地点所在时区的日历上解释：
    - anchor_date：可选，格式 YYYY-MM-DD，表示「第 0 天」是哪一天；省略则取当地「今天」的日期。
    - start_offset_days：从锚定日起向后跳几天作为预报窗口的第一天。例如锚定为今天时：1=明天，2=后天。
    - num_days：从窗口第一天起连续包含几个自然日。例如明天起共 8 天：start_offset_days=1, num_days=8。

    示例（假设锚定日为 2026-05-07）：
    - 只要明天：start_offset_days=1, num_days=1
    - 只要后天：start_offset_days=2, num_days=1
    - 大后天：start_offset_days=3, num_days=1
    - 从明天起一周（含 5/8～5/15 共 8 天）：start_offset_days=1, num_days=8

    location：城市名或「纬度,经度」。
    """
    try:
        if num_days < 1 or num_days > 16:
            return "num_days 须在 1～16 之间（Open-Meteo 预报长度限制）。"
        if start_offset_days < 0 or start_offset_days > 30:
            return "start_offset_days 须在 0～30 之间。"

        lat, lon, label = _resolve_coordinates(location)
        fc_days = min(16, max(1, start_offset_days + num_days + 1))
        fc_params = urllib.parse.urlencode(
            {
                "latitude": lat,
                "longitude": lon,
                "hourly": ",".join(
                    [
                        "temperature_2m",
                        "precipitation_probability",
                        "weathercode",
                        "relative_humidity_2m",
                        "windspeed_10m",
                    ]
                ),
                "forecast_days": fc_days,
                "timezone": "auto",
            }
        )
        fc = _http_get_json(f"https://api.open-meteo.com/v1/forecast?{fc_params}")
        tz_name = fc.get("timezone") or "UTC"
        tz = ZoneInfo(tz_name)

        anchor = _parse_anchor_date(anchor_date, tz)
        start_d = anchor + timedelta(days=start_offset_days)
        end_d = start_d + timedelta(days=num_days - 1)
        window_start = datetime.combine(start_d, time.min, tzinfo=tz)
        window_end_excl = datetime.combine(end_d + timedelta(days=1), time.min, tzinfo=tz)

        hourly = fc.get("hourly") or {}
        times: list[str] = hourly.get("time") or []
        temps: list[Optional[float]] = hourly.get("temperature_2m") or []
        pops: list[Optional[float]] = hourly.get("precipitation_probability") or []
        codes: list[Optional[float]] = hourly.get("weathercode") or []
        rh: list[Optional[float]] = hourly.get("relative_humidity_2m") or []
        wind: list[Optional[float]] = hourly.get("windspeed_10m") or []

        rows: list[
            tuple[datetime, Optional[float], Optional[float], Optional[float], Optional[float], Optional[float]]
        ] = []
        for i, t in enumerate(times):
            slot = datetime.fromisoformat(t)
            if slot.tzinfo is None:
                slot = slot.replace(tzinfo=tz)
            if window_start <= slot < window_end_excl:
                rows.append(
                    (
                        slot,
                        temps[i] if i < len(temps) else None,
                        pops[i] if i < len(pops) else None,
                        codes[i] if i < len(codes) else None,
                        rh[i] if i < len(rh) else None,
                        wind[i] if i < len(wind) else None,
                    )
                )

        if not rows:
            return (
                f"地点「{label}」({lat:.4f},{lon:.4f}) 在时区 {tz_name} 下，"
                f"{start_d.isoformat()}～{end_d.isoformat()} 没有可用预报数据（可能超出可预报范围）。"
            )

        header = [
            f"地点：{label} ({lat:.4f}, {lon:.4f})，时区：{tz_name}",
            f"锚定日：{anchor.isoformat()}，查询窗口：{start_d.isoformat()}～{end_d.isoformat()}（共 {num_days} 个自然日）",
        ]

        if num_days <= 2:
            lines = header + ["逐小时："]
            for slot, tp, po, wc, hr, ws in rows:
                lines.append(
                    f"  {slot.strftime('%Y-%m-%d %H:%M')} | "
                    f"{tp if tp is not None else '?'}°C | "
                    f"降水 {po if po is not None else '?'}% | "
                    f"{_weather_label(wc)} | "
                    f"湿度 {hr if hr is not None else '?'}% | "
                    f"风速 {ws if ws is not None else '?'} km/h"
                )
            return "\n".join(lines)

        by_day: dict[date, list[tuple]] = defaultdict(list)
        for r in rows:
            by_day[r[0].date()].append(r)

        lines = header + ["按日汇总："]
        for d in sorted(by_day.keys()):
            day_rows = by_day[d]
            tvals = [x[1] for x in day_rows if x[1] is not None]
            pvals = [x[2] for x in day_rows if x[2] is not None]
            cvals = [x[3] for x in day_rows if x[3] is not None]
            tmin = min(tvals) if tvals else None
            tmax = max(tvals) if tvals else None
            pmax = max(pvals) if pvals else None
            mode_code = None
            if cvals:
                freq: dict[int, int] = defaultdict(int)
                for c in cvals:
                    freq[int(round(c))] += 1
                mode_code = float(max(freq, key=lambda k: freq[k]))
            lines.append(
                f"  {d.isoformat()} | 气温 {tmin if tmin is not None else '?'}～{tmax if tmax is not None else '?'}°C | "
                f"降水概率峰值 {pmax if pmax is not None else '?'}% | {_weather_label(mode_code)}"
            )
        return "\n".join(lines)
    except urllib.error.URLError as e:
        return f"天气接口网络错误：{e}"
    except (ValueError, KeyError, TypeError) as e:
        return f"天气查询失败：{e}"
