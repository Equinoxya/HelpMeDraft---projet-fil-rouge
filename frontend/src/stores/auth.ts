import { defineStore } from "pinia";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    accessToken: null as string | null,
    user: null as { user_id: string; email: string } | null,
  }),
  getters: {
    isAuthenticated: (state) => state.accessToken !== null,
  },
  actions: {},
});
