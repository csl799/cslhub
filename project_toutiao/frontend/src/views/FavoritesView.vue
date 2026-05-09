<script setup lang="ts">
import { onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import { clearFavorites, fetchFavoriteList } from "@/api/favorite";
import type { FavoriteItem } from "@/types/news";
import NewsCard from "@/components/news/NewsCard.vue";

const list = ref<FavoriteItem[]>([]);
const page = ref(1);
const total = ref(0);
const hasMore = ref(false);
const loading = ref(false);
const errorMsg = ref("");

async function load(reset: boolean) {
  loading.value = true;
  errorMsg.value = "";
  if (reset) page.value = 1;
  try {
    const res = await fetchFavoriteList({ page: page.value, pageSize: 10 });
    if (reset) list.value = res.list;
    else list.value = [...list.value, ...res.list];
    total.value = res.total;
    hasMore.value = res.hasMore;
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : "加载失败";
  } finally {
    loading.value = false;
  }
}

async function loadMore() {
  if (!hasMore.value || loading.value) return;
  page.value += 1;
  await load(false);
}

async function onClear() {
  if (!list.value.length) return;
  if (!window.confirm("确定清空全部收藏？此操作不可恢复。")) return;
  loading.value = true;
  errorMsg.value = "";
  try {
    await clearFavorites();
    list.value = [];
    total.value = 0;
    hasMore.value = false;
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : "清空失败";
  } finally {
    loading.value = false;
  }
}

onMounted(() => load(true));
</script>

<template>
  <div class="favorites">
    <div class="toolbar">
      <h1 class="title">我的收藏</h1>
      <div class="actions">
        <span v-if="total" class="count">共 {{ total }} 条</span>
        <button
          type="button"
          class="btn-clear"
          :disabled="loading || !list.length"
          @click="onClear"
        >
          清空收藏
        </button>
      </div>
    </div>

    <p v-if="errorMsg" class="alert">{{ errorMsg }}</p>

    <div v-if="loading && !list.length" class="state">加载中…</div>
    <p v-else-if="!list.length" class="state">暂无收藏，去<RouterLink to="/">首页</RouterLink>逛逛吧</p>

    <div v-else class="list">
      <NewsCard
        v-for="item in list"
        :key="item.id"
        :item="item"
      />
    </div>

    <div v-if="hasMore" class="more-wrap">
      <button type="button" class="btn-more" :disabled="loading" @click="loadMore">
        {{ loading ? "加载中…" : "加载更多" }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.favorites {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}
.title {
  margin: 0;
  font-size: 1.35rem;
}
.actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.count {
  font-size: 0.875rem;
  color: var(--color-muted);
}
.btn-clear {
  border: 1px solid #ef9a9a;
  background: #fff;
  color: var(--color-accent);
  border-radius: 8px;
  padding: 0.35rem 0.9rem;
  font-size: 0.875rem;
}
.btn-clear:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.btn-clear:not(:disabled):hover {
  background: #ffebee;
}
.alert {
  margin: 0;
  padding: 0.75rem 1rem;
  background: #fff3e0;
  border-radius: var(--radius);
  color: #e65100;
}
.state {
  margin: 0;
  text-align: center;
  padding: 2rem;
  color: var(--color-muted);
}
.list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.more-wrap {
  display: flex;
  justify-content: center;
}
.btn-more {
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  border-radius: 8px;
  padding: 0.5rem 1.5rem;
}
.btn-more:disabled {
  opacity: 0.6;
}
</style>
