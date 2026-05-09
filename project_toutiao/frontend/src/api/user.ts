import { httpRequest } from "@/api/http";
import type { UserInfo } from "@/types/api";

export interface LoginRegisterPayload {
  username: string;
  password: string;
}

export interface AuthPayload {
  token: string;
  userInfo: UserInfo;
}

function unwrapAuth(data: unknown): AuthPayload {
  const d = data as Record<string, unknown>;
  const token = String(d.token ?? "");
  const userInfo = (d.userInfo ?? d.user_info) as UserInfo;
  if (!token || !userInfo) throw new Error("登录响应格式异常");
  return { token, userInfo };
}

export async function login(body: LoginRegisterPayload): Promise<AuthPayload> {
  const data = await httpRequest<unknown>("/api/user/login", {
    method: "POST",
    body: JSON.stringify(body),
  });
  return unwrapAuth(data);
}

export async function register(
  body: LoginRegisterPayload
): Promise<AuthPayload> {
  const data = await httpRequest<unknown>("/api/user/register", {
    method: "POST",
    body: JSON.stringify(body),
  });
  return unwrapAuth(data);
}

export async function fetchUserInfo(): Promise<UserInfo> {
  return httpRequest<UserInfo>("/api/user/info", { method: "GET", auth: true });
}
