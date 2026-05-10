export interface NewsSummary {
  id: number;
  title: string;
  description: string | null;
  image: string | null;
  author: string | null;
  publishTime: string | null;
  categoryId: number;
  views: number;
}

export interface NewsDetail extends NewsSummary {
  content: string;
  category: number;
  relatedNews: NewsSummary[];
}

export interface NewsCategory {
  id: number;
  name: string;
  sort_order?: number;
}

export interface FavoriteItem extends NewsSummary {
  favoritedAt: string | null;
}
