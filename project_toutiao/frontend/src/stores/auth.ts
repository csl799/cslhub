import { defineStore } from "pinia";
import { computed, ref } from "vue";
import { fetchUserInfo, login, register, type LoginRegisterPayload } from "@/api/user";
import { getStoredToken, setStoredToken } from "@/api/http";
import type { UserInfo } from "@/types/api";

export const useAuthStore = defineStore("auth", () => {
  const token = ref<string | null>(getStoredToken());
  const user = ref<UserInfo | null>(null);
  const loading = ref(false);

  const isLoggedIn = computed(() => Boolean(token.value));

  function setSession(nextToken: string, nextUser: UserInfo) {
    token.value = nextToken;
    user.value = nextUser;
    setStoredToken(nextToken);
  }

  function clearSession() {
    token.value = null;
    user.value = null;
    setStoredToken(null);
  }

  async function signIn(payload: LoginRegisterPayload) {
    loading.value = true;
    try {
      const res = await login(payload);
      setSession(res.token, res.userInfo);
    } finally {
      loading.value = false;
    }
  }

  async function signUp(payload: LoginRegisterPayload) {
    loading.value = true;
    try {
      const res = await register(payload);
      setSession(res.token, res.userInfo);
    } finally {
      loading.value = false;
    }
  }

  async function refreshProfile() {
    if (!token.value) return;
    loading.value = true;
    try {
      user.value = await fetchUserInfo();
    } finally {
      loading.value = false;
    }
  }

  function hydrateFromStorage() {
    token.value = getStoredToken();
  }

  return {
    token,
    user,
    loading,
    isLoggedIn,
    signIn,
    signUp,
    clearSession,
    refreshProfile,
    hydrateFromStorage,
  };
});
