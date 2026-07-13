import { defineStore } from "pinia";
import { login as loginApi } from "../services/authService";
import type { LoginPayload } from "../services/authService";

interface User {
  user_id: string;
  email: string;
  firstname: string;
  lastname: string;
}

export const useAuthStore = defineStore("auth", {
  state: () => ({
    accessToken: null as string | null,
    refreshToken: null as string | null,
    user: null as User | null,
  }),

  getters: {
    isAuthenticated: (state) => state.accessToken !== null,
  },

  actions: {
    async login(payload: LoginPayload) {
      const data = await loginApi(payload);

      this.accessToken = data.access_token;
      this.refreshToken = data.refresh_token;
      this.user = data.user;
    },

    logout() {
      this.accessToken = null;
      this.refreshToken = null;
      this.user = null;
    },
  },
});
