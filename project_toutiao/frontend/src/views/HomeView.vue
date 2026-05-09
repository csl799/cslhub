<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { fetchCategories, fetchNewsList } from "@/api/news";
import type { NewsCategory, NewsSummary } from "@/types/news";
import NewsCard from "@/components/news/NewsCard.vue";

const categories = ref<NewsCategory[]>([]);
const activeCategoryId = ref<number | null>(null);
const list = ref<NewsSummary[]>([]);
const page = ref(1);
const total = ref(0);
const hasMore = ref(false);
const loading = ref(false);
const errorMsg = ref("");

const sortedCategories = computed(() =>
  [...categories.value].sort(
    (a, b) => (a.sort_order ?? 0) - (b.sort_order ?? 0) || a.id - b.id
  )
);

async function loadCategories() {
  errorMsg.value = "";
  try {
    categories.value = await fetchCategories();
    if (!categories.value.length) {
      errorMsg.value = "暂无新闻分类";
      return;
    }
    if (
      activeCategoryId.value === null ||
      !categories.value.some((c) => c.id === activeCategoryId.value)
    ) {
      activeCategoryId.value = sortedCategories.value[0]?.id ?? null;
    }
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : "加载分类失败";
  }
}

async function loadList(reset: boolean) {
  if (activeCategoryId.value === null) return;
  loading.value = true;
  errorMsg.value = "";
  if (reset) {
    page.value = 1;
    list.value = [];
  }
  try {
    const res = await fetchNewsList({
      categoryId: activeCategoryId.value,
      page: page.value,
      pageSize: 10,
    });
    if (reset) list.value = res.list;
    else list.value = [...list.value, ...res.list];
    total.value = res.total;
    hasMore.value = res.hasMore;
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : "加载新闻失败";
  } finally {
    loading.value = false;
  }
}

function selectCategory(id: number) {
  activeCategoryId.value = id;
}

async function loadMore() {
  if (!hasMore.value || loading.value) return;
  page.value += 1;
  loading.value = true;
  errorMsg.value = "";
  try {
    const res = await fetchNewsList({
      categoryId: activeCategoryId.value!,
      page: page.value,
      pageSize: 10,
    });
    list.value = [...list.value, ...res.list];
    total.value = res.total;
    hasMore.value = res.hasMore;
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : "加载更多失败";
    page.value -= 1;
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  await loadCategories();
});

watch(activeCategoryId, async (id) => {
  if (id !== null) await loadList(true);
});
</script>

<template>
  <div class="home">
    <p v-if="errorMsg" class="alert">{{ errorMsg }}</p>

    <section v-if="sortedCategories.length" class="tabs">
      <button
        v-for="c in sortedCategories"
        :key="c.id"
        type="button"
        class="tab"
        :class="{ active: c.id === activeCategoryId }"
        @click="selectCategory(c.id)"
      >
        {{ c.name }}
      </button>
    </section>

    <p v-if="activeCategoryId !== null && total" class="hint">共 {{ total }} 条</p>

    <div class="list">
      <NewsCard v-for="item in list" :key="item.id" :item="item" />
    </div>

    <div v-if="loading && !list.length" class="state">加载中…</div>
    <div v-else-if="!list.length && !loading && activeCategoryId" class="state">
      该分类下暂无新闻
    </div>

    <div v-if="hasMore" class="more-wrap">
      <button type="button" class="btn-more" :disabled="loading" @click="loadMore">
        {{ loading ? "加载中…" : "加载更多" }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.alert {
  margin: 0;
  padding: 0.75rem 1rem;
  background: #fff3e0;
  border: 1px solid #ffcc80;
  border-radius: var(--radius);
  color: #e65100;
}
.tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.tab {
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  border-radius: 999px;
  padding: 0.4rem 1rem;
  font-size: 0.875rem;
  color: var(--color-muted);
}
.tab:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
}
.tab.active {
  background: var(--color-accent);
  color: #fff;
  border-color: var(--color-accent);
}
.hint {
  margin: 0;
  font-size: 0.8125rem;
  color: var(--color-muted);
}
.list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.state {
  text-align: center;
  padding: 2rem;
  color: var(--color-muted);
}
.more-wrap {
  display: flex;
  justify-content: center;
  padding: 0.5rem 0 1rem;
}
.btn-more {
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  border-radius: 8px;
  padding: 0.5rem 1.5rem;
  color: var(--color-text);
}
.btn-more:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.btn-more:not(:disabled):hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
}
</style>
