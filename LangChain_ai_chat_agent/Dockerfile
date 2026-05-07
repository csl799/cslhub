# 应用镜像：FastAPI + LangChain（需连接 MySQL）
FROM python:3.12-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# 0.0.0.0 才可在容器外访问；生产环境建议前面再加 Nginx/Caddy 做 HTTPS
CMD ["uvicorn", "web.app:app", "--host", "0.0.0.0", "--port", "8000"]
