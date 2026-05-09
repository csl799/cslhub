<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const route = useRoute();
const router = useRouter();

const username = ref("");
const password = ref("");
const mode = ref<"login" | "register">("login");
const errorMsg = ref("");

onMounted(() => {
  if (auth.isLoggedIn) {
    router.replace(typeof route.query.redirect === "string" ? route.query.redirect : "/");
  }
});

async function submit() {
  errorMsg.value = "";
  if (!username.value.trim() || !password.value) {
    errorMsg.value = "请输入用户名和密码";
    return;
  }
  try {
    if (mode.value === "login") {
      await auth.signIn({
        username: username.value.trim(),
        password: password.value,
      });
    } else {
      await auth.signUp({
        username: username.value.trim(),
        password: password.value,
      });
    }
    const redirect =
      typeof route.query.redirect === "string" ? route.query.redirect : "/";
    await router.replace(redirect || "/");
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : "操作失败";
  }
}

function switchMode(m: "login" | "register") {
  mode.value = m;
  errorMsg.value = "";
}
</script>

<template>
  <div class="login-page">
    <div class="card">
      <h1 class="title">{{ mode === "login" ? "登录" : "注册" }}</h1>
      <p v-if="errorMsg" class="alert">{{ errorMsg }}</p>
      <form class="form" @submit.prevent="submit">
        <label class="field">
          <span>用户名</span>
          <input v-model="username" type="text" autocomplete="username" required />
        </label>
        <label class="field">
          <span>密码</span>
          <input
            v-model="password"
            type="password"
            autocomplete="current-password"
            required
          />
        </label>
        <button type="submit" class="submit" :disabled="auth.loading">
          {{ auth.loading ? "请稍候…" : mode === "login" ? "登录" : "注册" }}
        </button>
      </form>
      <p class="switch">
        <template v-if="mode === 'login'">
          没有账号？
          <button type="button" class="linkish" @click="switchMode('register')">注册</button>
        </template>
        <template v-else>
          已有账号？
          <button type="button" class="linkish" @click="switchMode('login')">登录</button>
        </template>
      </p>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  padding-top: 2rem;
}
.card {
  width: 100%;
  max-width: 400px;
  background: var(--color-surface);
  border-radius: var(--radius);
  border: 1px solid var(--color-border);
  padding: 1.5rem 1.75rem;
  box-shadow: var(--shadow);
}
.title {
  margin: 0 0 1rem;
  font-size: 1.25rem;
  text-align: center;
}
.alert {
  margin: 0 0 1rem;
  padding: 0.6rem 0.75rem;
  background: #ffebee;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #c62828;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.875rem;
  color: var(--color-muted);
}
.field input {
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 0.5rem 0.75rem;
  font: inherit;
}
.submit {
  margin-top: 0.25rem;
  border: none;
  border-radius: 8px;
  padding: 0.6rem;
  background: var(--color-accent);
  color: #fff;
  font-weight: 600;
}
.submit:disabled {
  opacity: 0.65;
}
.switch {
  margin: 1.25rem 0 0;
  text-align: center;
  font-size: 0.875rem;
  color: var(--color-muted);
}
.linkish {
  border: none;
  background: none;
  padding: 0;
  color: var(--color-accent);
  font: inherit;
  cursor: pointer;
  text-decoration: underline;
}
</style>
