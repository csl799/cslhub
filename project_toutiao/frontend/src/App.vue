<script setup lang="ts">
import { onMounted } from "vue";
import AppHeader from "@/components/layout/AppHeader.vue";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
onMounted(() => {
  auth.hydrateFromStorage();
  if (auth.token) {
    auth.refreshProfile().catch(() => {});
  }
});
</script>

<template>
  <div class="app-root">
    <AppHeader />
    <main class="app-main">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.app-root {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-bg);
}
.app-main {
  flex: 1;
  width: 100%;
  max-width: 960px;
  margin: 0 auto;
  padding: 1rem 1.25rem 2.5rem;
}
</style>
