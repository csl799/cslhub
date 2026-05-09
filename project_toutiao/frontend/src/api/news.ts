import { httpRequest } from "@/api/http";
import type { NewsCategory, NewsDetail, NewsSummary } from "@/types/news";
import { normalizeNewsSummary } from "@/utils/news";

export async function fetchCategories(): Promise<NewsCategory[]> {
  const data = await httpRequest<NewsCategory[]>("/api/news/categories");
  return Array.isArray(data) ? data : [];
}

export async function fetchNewsList(params: {
  categoryId: number;
  page?: number;
  pageSize?: number;
}): Promise<{ list: NewsSummary[]; total: number; hasMore: boolean }> {
  const page = params.page ?? 1;
  const pageSize = params.pageSize ?? 10;
  const q = new URLSearchParams({
    categoryId: String(params.categoryId),
    page: String(page),
    pageSize: String(pageSize),
  });
  const data = await httpRequest<{
    list: Record<string, unknown>[];
    total: number;
    hasMore: boolean;
  }>(`/api/news/list?${q.toString()}`);
  const list = (data?.list ?? []).map((row) => normalizeNewsSummary(row));
  return {
    list,
    total: Number(data?.total ?? 0),
    hasMore: Boolean(data?.hasMore),
  };
}

export async function fetchNewsDetail(id: number): Promise<NewsDetail> {
  const q = new URLSearchParams({ id: String(id) });
  const raw = await httpRequest<Record<string, unknown>>(
    `/api/news/detail?${q.toString()}`
  );
  const base = normalizeNewsSummary({
    ...raw,
    category_id: raw.category ?? raw.category_id,
  });
  const relatedRaw = (raw.relatedNews ?? raw.related_news) as
    | Record<string, unknown>[]
    | undefined;
  const relatedNews = (relatedRaw ?? []).map((r) => normalizeNewsSummary(r));
  return {
    ...base,
    content: String(raw.content ?? ""),
    category: Number(raw.category ?? raw.category_id ?? 0),
    relatedNews,
  };
}
