import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "./stores/auth.ts";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/login",
      name: "login",
      component: () => import("./views/LoginView.vue"),
      meta: { guestOnly: true },
    },
    {
      path: "/dashboard",
      name: "dashboard",
      component: () => import("./views/DashboardView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/register",
      name: "register",
      component: () => import("./views/RegisterView.vue"),
      meta: { guestOnly: true },
    },
    {
      path: "/forgot-password",
      name: "ForgotPassword",
      component: () => import("./views/ForgotPasswordView.vue"),
      meta: { guestOnly: true },
    },
    {
      path: "/reset-password",
      name: "ResetPassword",
      component: () => import("./views/ResetPasswordView.vue"),
      meta: { guestOnly: true },
    },
  ],
});

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();

  if (!authStore.isInitialized) {
    await authStore.initialize();
  }
  const isAuthenticated = !!authStore.accessToken;
  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: "login" });
  } else if (to.meta.guestOnly && isAuthenticated) {
    next({ name: "dashboard" });
  } else {
    next();
  }
});
export default router;
