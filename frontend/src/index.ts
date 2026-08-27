import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "./stores/auth.ts";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "home",
      component: () => import("./views/HomeView.vue"),
    },
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
    {
      path: "/mentions-legales",
      name: "MentionsLegales",
      component: () => import("./views/MentionsLegalesView.vue"),
    },
    {
      path: "/cgu",
      name: "CGU",
      component: () => import("./views/CguView.vue"),
    },
    {
      path: "/confidentialite",
      name: "Confidentialite",
      component: () => import("./views/ConfidentialiteView.vue"),
    },
    {
      path: "/documents",
      name: "documents-list",
      component: () => import("./views/DocumentsListView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/documents/nouveau",
      name: "document-new",
      component: () => import("./views/DocumentEditorView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/documents/:id",
      name: "document-edit",
      component: () => import("./views/DocumentEditorView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/fonctionnalites",
      name: "fonctionnalites",
      component: () => import("./views/FonctionnalitesView.vue"),
    },
    {
      path: "/tarifs",
      name: "tarifs",
      component: () => import("./views/TarifsView.vue"),
    },
    {
      path: "/modeles",
      name: "modeles",
      component: () => import("./views/ModelesView.vue"),
    },
  ],
  scrollBehavior() {
    // Remonte en haut de page quand on clique sur un lien du footer
    return { top: 0 };
  },
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
