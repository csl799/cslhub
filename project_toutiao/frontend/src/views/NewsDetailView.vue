<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { RouterLink, useRoute } from "vue-router";
import { fetchNewsDetail } from "@/api/news";
import {
  addFavorite,
  fetchFavoriteStatus,
  removeFavorite,
} from "@/api/favorite";
import { useAuthStore } from "@/stores/auth";
import type { NewsDetail } from "@/types/news";
import { formatDateTime } from "@/utils/format";
import NewsCard from "@/components/news/NewsCard.vue";

const route = useRoute();
const auth = useAuthStore();

const detail = ref<NewsDetail | null>(null);
const loading = ref(true);
const errorMsg = ref("");
const favorited = ref(false);
const favoriteLoading = ref(false);

const newsId = computed(() => Number(route.params.id));

async function load() {
  loading.value = true;
  errorMsg.value = "";
  detail.value = null;
  try {
    detail.value = await fetchNewsDetail(newsId.value);
    if (auth.isLoggedIn) {
      favorited.value = await fetchFavoriteStatus(newsId.value);
    } else {
      favorited.value = false;
    }
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : "加载失败";
  } finally {
    loading.value = false;
  }
}

async function toggleFavorite() {
  if (!auth.isLoggedIn) {
    errorMsg.value = "请先登录后再收藏";
    return;
  }
  favoriteLoading.value = true;
  try {
    if (favorited.value) {
      await removeFavorite(newsId.value);
      favorited.value = false;
    } else {
      await addFavorite(newsId.value);
      favorited.value = true;
    }
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : "收藏操作失败";
  } finally {
    favoriteLoading.value = false;
  }
}

onMounted(load);
watch(newsId, load);
watch(
  () => auth.isLoggedIn,
  async (loggedIn) => {
    if (!detail.value) return;
    if (loggedIn) {
      try {
        favorited.value = await fetchFavoriteStatus(newsId.value);
      } catch {
        favorited.value = false;
      }
    } else favorited.value = false;
  }
);
</script>

<template>
  <div class="detail">
    <RouterLink to="/" class="back">← 返回首页</RouterLink>

    <p v-if="errorMsg" class="alert">{{ errorMsg }}</p>
    <p v-if="loading" class="state">加载中…</p>

    <article v-else-if="detail" class="article">
      <header class="head">
        <h1 class="title">{{ detail.title }}</h1>
        <div class="meta">
          <span v-if="detail.author">{{ detail.author }}</span>
          <span>{{ formatDateTime(detail.publishTime) }}</span>
          <span>阅读 {{ detail.views }}</span>
        </div>
        <div class="actions">
          <button
            type="button"
            class="fav-btn"
            :disabled="favoriteLoading"
            @click="toggleFavorite"
          >
            {{ favorited ? "★ 已收藏" : "☆ 收藏" }}
          </button>
        </div>
      </header>
      <img v-if="detail.image" :src="detail.image" :alt="detail.title" class="cover" />
      <div class="content">{{ detail.content }}</div>

      <section v-if="detail.relatedNews?.length" class="related">
        <h2>相关新闻</h2>
        <div class="related-list">
          <NewsCard v-for="r in detail.relatedNews" :key="r.id" :item="r" />
        </div>
      </section>
    </article>
  </div>
</template>

<style scoped>
.detail {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.back {
  font-size: 0.875rem;
  color: var(--color-muted);
  text-decoration: none;
  align-self: flex-start;
}
.back:hover {
  color: var(--color-accent);
}
.alert {
  margin: 0;
  padding: 0.75rem 1rem;
  background: #fff3e0;
  border-radius: var(--radius);
  color: #e65100;
}
.state {
  text-align: center;
  padding: 2rem;
  color: var(--color-muted);
}
.article {
  background: var(--color-surface);
  border-radius: var(--radius);
  border: 1px solid var(--color-border);
  padding: 1.25rem 1.5rem;
  box-shadow: var(--shadow);
}
.head {
  margin-bottom: 1rem;
}
.title {
  margin: 0 0 0.5rem;
  font-size: 1.5rem;
  line-height: 1.35;
}
.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  font-size: 0.875rem;
  color: var(--color-muted);
  margin-bottom: 0.75rem;
}
.actions {
  display: flex;
  gap: 0.5rem;
}
.fav-btn {
  border: 1px solid var(--color-border);
  background: #fff8f8;
  border-radius: 8px;
  padding: 0.4rem 1rem;
  color: var(--color-accent);
  font-weight: 500;
}
.fav-btn:disabled {
  opacity: 0.6;
}
.cover {
  width: 100%;
  max-height: 360px;
  object-fit: cover;
  border-radius: 8px;
  margin-bottom: 1rem;
}
.content {
  font-size: 1rem;
  line-height: 1.75;
  word-break: break-word;
  white-space: pre-wrap;
}
.related {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--color-border);
}
.related h2 {
  margin: 0 0 1rem;
  font-size: 1.125rem;
}
.related-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
</style>
