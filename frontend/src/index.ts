import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "./stores/auth.ts";

// `meta.titre` est déclaré ici plutôt que laissé en `unknown` : sans cette
// augmentation, une faute de frappe dans une route ne se verrait qu'à
// l'exécution, sous la forme d'un titre manquant.
declare module "vue-router" {
  interface RouteMeta {
    titre?: string;
    requiresAuth?: boolean;
    requiresAdmin?: boolean;
    guestOnly?: boolean;
  }
}

const NOM_APPLICATION = "HelpMeDraft";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "home",
      component: () => import("./views/HomeView.vue"),
      meta: { titre: "Accueil" },
    },
    {
      path: "/login",
      name: "login",
      component: () => import("./views/LoginView.vue"),
      meta: { titre: "Connexion", guestOnly: true },
    },
    {
      path: "/dashboard",
      name: "dashboard",
      component: () => import("./views/DashboardView.vue"),
      meta: { titre: "Tableau de bord", requiresAuth: true },
    },
    {
      path: "/register",
      name: "register",
      component: () => import("./views/RegisterView.vue"),
      meta: { titre: "Inscription", guestOnly: true },
    },
    {
      path: "/forgot-password",
      name: "ForgotPassword",
      component: () => import("./views/ForgotPasswordView.vue"),
      meta: { titre: "Mot de passe oublié", guestOnly: true },
    },
    {
      path: "/reset-password",
      name: "ResetPassword",
      component: () => import("./views/ResetPasswordView.vue"),
      meta: { titre: "Nouveau mot de passe", guestOnly: true },
    },
    {
      path: "/mentions-legales",
      name: "MentionsLegales",
      component: () => import("./views/MentionsLegalesView.vue"),
      meta: { titre: "Mentions légales" },
    },
    {
      path: "/cgu",
      name: "CGU",
      component: () => import("./views/CguView.vue"),
      meta: { titre: "Conditions générales d'utilisation" },
    },
    {
      path: "/confidentialite",
      name: "Confidentialite",
      component: () => import("./views/ConfidentialiteView.vue"),
      meta: { titre: "Politique de confidentialité" },
    },
    {
      path: "/documents",
      name: "documents-list",
      component: () => import("./views/DocumentsListView.vue"),
      meta: { titre: "Mes documents", requiresAuth: true },
    },
    {
      path: "/documents/nouveau",
      name: "document-new",
      component: () => import("./views/DocumentEditorView.vue"),
      meta: { titre: "Nouveau document", requiresAuth: true },
    },
    {
      path: "/documents/:id",
      name: "document-edit",
      component: () => import("./views/DocumentEditorView.vue"),
      meta: { titre: "Édition d'un document", requiresAuth: true },
    },
    {
      path: "/fonctionnalites",
      name: "fonctionnalites",
      component: () => import("./views/FonctionnalitesView.vue"),
      meta: { titre: "Fonctionnalités" },
    },
    {
      path: "/tarifs",
      name: "tarifs",
      component: () => import("./views/TarifsView.vue"),
      meta: { titre: "Tarifs" },
    },
    {
      path: "/modeles",
      name: "modeles",
      component: () => import("./views/ModelesView.vue"),
      meta: { titre: "Modèles de documents" },
    },
    {
      path: "/admin",
      name: "admin",
      component: () => import("./views/AdminView.vue"),
      meta: {
        titre: "Administration",
        requiresAuth: true,
        requiresAdmin: true,
      },
    },
  ],
  scrollBehavior() {
    // Remonte en haut de page quand on clique sur un lien du footer
    return { top: 0 };
  },
});

router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore();
  if (!authStore.isInitialized) {
    await authStore.initialize();
  }
  const isAuthenticated = !!authStore.accessToken;
  const isAdmin = authStore.user?.role === "admin";

  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: "login" });
  } else if (to.meta.requiresAdmin && !isAdmin) {
    next({ name: "dashboard" });
  } else if (to.meta.guestOnly && isAuthenticated) {
    next({ name: "dashboard" });
  } else {
    next();
  }
});
// RGAA 8.6 — les 16 écrans partageaient le même <title>, ce qui rend la liste
// des onglets et l'historique du navigateur illisibles pour qui navigue au
// lecteur d'écran. Le titre est posé après la navigation, et non dans chaque
// vue : une vue qui oublierait de le faire laisserait celui de la page
// précédente.
router.afterEach((to) => {
  document.title = to.meta.titre
    ? `${to.meta.titre} — ${NOM_APPLICATION}`
    : NOM_APPLICATION;
});

export default router;
