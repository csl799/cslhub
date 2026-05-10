import type { NewsSummary } from "@/types/news";

export function normalizeNewsSummary(raw: Record<string, unknown>): NewsSummary {
  const id = Number(raw.id);
  const categoryId = Number(raw.categoryId ?? raw.category_id ?? 0);
  const publishTime =
    (raw.publishTime ?? raw.publish_time) as string | null | undefined;
  return {
    id,
    title: String(raw.title ?? ""),
    description: (raw.description as string | null) ?? null,
    image: (raw.image as string | null) ?? null,
    author: (raw.author as string | null) ?? null,
    publishTime: publishTime ?? null,
    categoryId,
    views: Number(raw.views ?? 0),
  };
}
