<script setup lang="ts">
import { RouterLink } from "vue-router";
import type { NewsSummary } from "@/types/news";
import { formatDateTime } from "@/utils/format";

defineProps<{
  item: NewsSummary;
}>();
</script>

<template>
  <article class="card">
    <RouterLink :to="{ name: 'news-detail', params: { id: item.id } }" class="thumb-wrap">
      <img v-if="item.image" :src="item.image" :alt="item.title" class="thumb" />
      <div v-else class="thumb placeholder">无图</div>
    </RouterLink>
    <div class="body">
      <RouterLink :to="{ name: 'news-detail', params: { id: item.id } }" class="title">
        {{ item.title }}
      </RouterLink>
      <p v-if="item.description" class="desc">{{ item.description }}</p>
      <div class="meta">
        <span v-if="item.author">{{ item.author }}</span>
        <span>{{ formatDateTime(item.publishTime) }}</span>
        <span>阅读 {{ item.views }}</span>
      </div>
    </div>
  </article>
</template>

<style scoped>
.card {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: var(--color-surface);
  border-radius: var(--radius);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow);
}
.thumb-wrap {
  flex-shrink: 0;
  width: 120px;
  border-radius: 8px;
  overflow: hidden;
  align-self: flex-start;
}
.thumb {
  width: 120px;
  height: 80px;
  object-fit: cover;
  display: block;
}
.placeholder {
  width: 120px;
  height: 80px;
  background: #eee;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  color: var(--color-muted);
}
.body {
  min-width: 0;
  flex: 1;
}
.title {
  font-weight: 600;
  font-size: 1rem;
  color: var(--color-text);
  text-decoration: none;
  display: block;
  margin-bottom: 0.35rem;
}
.title:hover {
  color: var(--color-accent);
}
.desc {
  margin: 0 0 0.5rem;
  font-size: 0.875rem;
  color: var(--color-muted);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  font-size: 0.8125rem;
  color: var(--color-muted);
}
</style>
