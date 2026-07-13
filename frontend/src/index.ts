import { createRouter, createWebHistory } from "vue-router";
import LoginView from "./views/LoginView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/login",
      name: "/login",
      component: LoginView,
    },
    {
      path: "/dashboard",
      name: "dashboard",
      component: () => import("./views/DashboardView.vue"),
    },
  ],
});

export default router;
