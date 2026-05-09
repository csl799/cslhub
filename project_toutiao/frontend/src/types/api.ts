export interface ApiEnvelope<T> {
  code: number;
  message: string;
  data: T;
}

export interface UserInfo {
  id: number;
  username: string;
  nickname: string | null;
  avatar: string | null;
  gender: string | null;
  bio: string | null;
}

export class ApiError extends Error {
  constructor(
    message: string,
    readonly statusCode: number,
    readonly bodyCode?: number
  ) {
    super(message);
    this.name = "ApiError";
  }
}
