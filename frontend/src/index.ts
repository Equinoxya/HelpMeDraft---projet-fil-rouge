import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/login",
      name: "login",
      component: () => import("./views/LoginView.vue"),
    },
    {
      path: "/dashboard",
      name: "dashboard",
      component: () => import("./views/DashboardView.vue"),
    },
    {
      path: "/register",
      name: "register",
      component: () => import("./views/RegisterView.vue"),
    },
  ],
});

export default router;
