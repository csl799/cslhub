import { httpRequest } from "@/api/http";
import type { FavoriteItem } from "@/types/news";

export async function fetchFavoriteStatus(
  newsId: number
): Promise<boolean> {
  const q = new URLSearchParams({ newsId: String(newsId) });
  const data = await httpRequest<{ favorited: boolean }>(
    `/api/favorite/status?${q.toString()}`,
    { method: "GET", auth: true }
  );
  return Boolean(data?.favorited);
}

export async function addFavorite(newsId: number): Promise<void> {
  await httpRequest<null>("/api/favorite/add", {
    method: "POST",
    auth: true,
    body: JSON.stringify({ newsId }),
  });
}

export async function removeFavorite(newsId: number): Promise<void> {
  const q = new URLSearchParams({ newsId: String(newsId) });
  await httpRequest<null>(`/api/favorite/remove?${q.toString()}`, {
    method: "DELETE",
    auth: true,
  });
}

export async function fetchFavoriteList(params: {
  page?: number;
  pageSize?: number;
}): Promise<{ list: FavoriteItem[]; total: number; hasMore: boolean }> {
  const page = params.page ?? 1;
  const pageSize = params.pageSize ?? 10;
  const q = new URLSearchParams({
    page: String(page),
    pageSize: String(pageSize),
  });
  return httpRequest<{ list: FavoriteItem[]; total: number; hasMore: boolean }>(
    `/api/favorite/list?${q.toString()}`,
    { method: "GET", auth: true }
  );
}

export async function clearFavorites(): Promise<number> {
  const data = await httpRequest<{ removed: number }>("/api/favorite/clear", {
    method: "DELETE",
    auth: true,
  });
  return Number(data?.removed ?? 0);
}
