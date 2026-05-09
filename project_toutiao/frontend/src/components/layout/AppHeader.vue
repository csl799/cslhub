<script setup lang="ts">
import { RouterLink, useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();

function logout() {
  auth.clearSession();
  router.push({ name: "home" });
}
</script>

<template>
  <header class="header">
    <div class="header-inner">
      <RouterLink class="brand" to="/">新闻阅读</RouterLink>
      <nav class="nav">
        <RouterLink to="/" :class="{ active: route.name === 'home' }">首页</RouterLink>
        <RouterLink to="/favorites" :class="{ active: route.name === 'favorites' }"
          >我的收藏</RouterLink
        >
        <template v-if="auth.isLoggedIn">
          <span class="user">{{ auth.user?.nickname || auth.user?.username }}</span>
          <button type="button" class="btn ghost" @click="logout">退出</button>
        </template>
        <RouterLink v-else class="btn" to="/login">登录</RouterLink>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.header {
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  box-shadow: var(--shadow);
}
.header-inner {
  max-width: 960px;
  margin: 0 auto;
  padding: 0.75rem 1.25rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}
.brand {
  font-weight: 700;
  font-size: 1.125rem;
  color: var(--color-text);
  text-decoration: none;
}
.brand:hover {
  color: var(--color-accent);
  text-decoration: none;
}
.nav {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  font-size: 0.9375rem;
}
.nav a {
  color: var(--color-muted);
  text-decoration: none;
}
.nav a:hover {
  color: var(--color-text);
}
.nav a.active {
  color: var(--color-accent);
  font-weight: 600;
}
.user {
  color: var(--color-muted);
  font-size: 0.875rem;
}
.btn {
  border: none;
  border-radius: 8px;
  padding: 0.35rem 0.85rem;
  background: var(--color-accent);
  color: #fff;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
}
.btn:hover {
  background: var(--color-accent-hover);
  text-decoration: none;
  color: #fff;
}
.btn.ghost {
  background: transparent;
  color: var(--color-muted);
  border: 1px solid var(--color-border);
}
.btn.ghost:hover {
  color: var(--color-text);
  border-color: var(--color-muted);
}
</style>
