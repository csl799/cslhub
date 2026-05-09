import { ApiError, type ApiEnvelope } from "@/types/api";

const TOKEN_KEY = "news_app_token";

export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setStoredToken(token: string | null): void {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

async function parseJson(res: Response): Promise<unknown> {
  const text = await res.text();
  if (!text) return null;
  try {
    return JSON.parse(text) as unknown;
  } catch {
    return { code: res.status, message: text, data: null };
  }
}

export async function httpRequest<T>(
  path: string,
  init: RequestInit & { auth?: boolean } = {}
): Promise<T> {
  const { auth = false, headers: hdr, ...rest } = init;
  const headers = new Headers(hdr);
  if (!headers.has("Content-Type") && rest.body) {
    headers.set("Content-Type", "application/json");
  }
  if (auth) {
    const token = getStoredToken();
    if (token) headers.set("Authorization", `Bearer ${token}`);
  }

  const res = await fetch(path, { ...rest, headers });
  const body = (await parseJson(res)) as ApiEnvelope<unknown> | null;

  if (body && typeof body === "object" && "code" in body) {
    const envelope = body as ApiEnvelope<T>;
    if (envelope.code !== 200) {
      throw new ApiError(
        envelope.message || "请求失败",
        res.status,
        envelope.code
      );
    }
    return envelope.data as T;
  }

  if (!res.ok) {
    throw new ApiError(
      (body as { message?: string })?.message || res.statusText,
      res.status
    );
  }

  return body as T;
}
