import axios from "axios";
import { useAuthStore } from "../stores/auth";
import router from "../index.ts";

const api = axios.create({
  baseURL: "http://localhost:5000/auth", // adapte à ton URL backend
  withCredentials: true, // essentiel pour envoyer le cookie httpOnly
});

// --- Intercepteur de requête : injecte le access token ---
api.interceptors.request.use((config) => {
  const authStore = useAuthStore();
  if (authStore.accessToken) {
    config.headers.Authorization = `Bearer ${authStore.accessToken}`;
  }
  return config;
});

// --- Gestion de la mutualisation des refresh en cours ---
let isRefreshing = false;
let refreshSubscribers: Array<(token: string) => void> = [];

function subscribeTokenRefresh(callback: (token: string) => void) {
  refreshSubscribers.push(callback);
}

function onRefreshed(token: string) {
  refreshSubscribers.forEach((callback) => callback(token));
  refreshSubscribers = [];
}

// --- Intercepteur de réponse : gère le 401 ---
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const authStore = useAuthStore();

    // On ne tente le refresh que si :
    // - c'est bien une 401
    // - la requête n'a pas déjà été rejouée (évite boucle infinie)
    // - ce n'est pas la route /refresh elle-même qui échoue (sinon boucle infinie aussi)
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url?.includes("/refresh")
    ) {
      if (isRefreshing) {
        // Un refresh est déjà en cours : on met la requête en attente
        return new Promise((resolve) => {
          subscribeTokenRefresh((newToken: string) => {
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            resolve(api(originalRequest));
          });
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        await authStore.initialize(); // réutilise ta logique de tryRefresh existante
        const newToken = authStore.accessToken;

        if (!newToken) {
          throw new Error("Refresh échoué : pas de nouveau token");
        }

        isRefreshing = false;
        onRefreshed(newToken);

        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return api(originalRequest);
      } catch (refreshError) {
        isRefreshing = false;
        refreshSubscribers = [];
        authStore.clearAuth();
        router.push({ name: "login" });
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  },
);

export default api;
