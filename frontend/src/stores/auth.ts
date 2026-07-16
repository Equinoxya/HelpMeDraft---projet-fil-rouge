import { defineStore } from "pinia";
import authService from "../services/authService";
import type { LoginPayload } from "../types/auth";

interface User {
  id: string;
  email: string;
}

export const useAuthStore = defineStore("auth", {
  state: () => ({
    accessToken: null as string | null,
    user: null as User | null,
    isInitialized: false,
  }),

  getters: {
    isAuthenticated: (state) => state.accessToken !== null,
  },

  actions: {
    async login(payload: LoginPayload) {
      const data = await authService.login(payload);
      this.accessToken = data.access_token;
      this.user = data.user;
    },

    async logout() {
      try {
        await authService.logout();
      } finally {
        this.accessToken = null;
        this.user = null;
      }
    },

    async tryRefresh(): Promise<boolean> {
      try {
        const data = await authService.refresh();
        this.accessToken = data.access_token;
        return true;
      } catch {
        this.accessToken = null;
        this.user = null;
        return false;
      }
    },

    async initialize() {
      await this.tryRefresh();
      this.isInitialized = true;
    },
  },
});
