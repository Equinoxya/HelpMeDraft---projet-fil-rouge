/**
 * Tests du magasin de session — TU-F08.
 *
 * Le magasin est la seule source de vérité sur la session côté client.
 * Deux propriétés comptent : l'access token ne doit jamais quitter la
 * mémoire pour `localStorage`, et un échec de renouvellement doit laisser
 * un état propre plutôt qu'une session à moitié ouverte.
 */
import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../../services/authService", () => ({
  default: {
    login: vi.fn(),
    logout: vi.fn(),
    refresh: vi.fn(),
    me: vi.fn(),
  },
}));

import authService from "../../services/authService";
import { useAuthStore } from "../auth";

const UTILISATEUR = {
  id: "u-1",
  email: "camille@exemple.fr",
  firstname: "Camille",
  lastname: "Dupont",
  role: "user" as const,
};

beforeEach(() => {
  setActivePinia(createPinia());
  vi.clearAllMocks();
  localStorage.clear();
});

describe("état initial", () => {
  it("démarre sans session", () => {
    const magasin = useAuthStore();
    expect(magasin.accessToken).toBeNull();
    expect(magasin.user).toBeNull();
    expect(magasin.isAuthenticated).toBe(false);
    expect(magasin.isInitialized).toBe(false);
  });
});

describe("connexion", () => {
  it("retient le jeton et l'identité", async () => {
    vi.mocked(authService.login).mockResolvedValue({
      access_token: "jeton-abc",
      user: UTILISATEUR,
    } as never);

    const magasin = useAuthStore();
    await magasin.login({ email: UTILISATEUR.email, mdp: "MotDePasse1" } as never);

    expect(magasin.accessToken).toBe("jeton-abc");
    expect(magasin.user).toEqual(UTILISATEUR);
    expect(magasin.isAuthenticated).toBe(true);
  });

  it("ne range jamais le jeton dans le stockage du navigateur", async () => {
    /**
     * Le jeton d'accès reste une variable JavaScript. Dans `localStorage`,
     * il serait lisible par tout script de la page : un XSS l'exfiltrerait.
     * C'est la contrepartie assumée du cookie HttpOnly pour le jeton de
     * rafraîchissement, et ce test empêche de revenir en arrière par
     * commodité.
     */
    vi.mocked(authService.login).mockResolvedValue({
      access_token: "jeton-abc",
      user: UTILISATEUR,
    } as never);

    await useAuthStore().login({ email: UTILISATEUR.email, mdp: "MotDePasse1" } as never);

    const stockage = JSON.stringify({
      local: { ...localStorage },
      session: { ...sessionStorage },
    });
    expect(stockage).not.toContain("jeton-abc");
  });
});

describe("clearAuth", () => {
  it("TU-F08 · remet la session à zéro", () => {
    const magasin = useAuthStore();
    magasin.accessToken = "jeton-abc";
    magasin.user = UTILISATEUR;

    magasin.clearAuth();

    expect(magasin.accessToken).toBeNull();
    expect(magasin.user).toBeNull();
    expect(magasin.isAuthenticated).toBe(false);
  });
});

describe("déconnexion", () => {
  it("vide la session après l'appel au serveur", async () => {
    vi.mocked(authService.logout).mockResolvedValue(undefined as never);

    const magasin = useAuthStore();
    magasin.accessToken = "jeton-abc";
    magasin.user = UTILISATEUR;

    await magasin.logout();

    expect(authService.logout).toHaveBeenCalled();
    expect(magasin.accessToken).toBeNull();
  });

  it("vide la session même si l'appel au serveur échoue", async () => {
    // Le `finally` du magasin : un serveur injoignable ne doit pas laisser
    // l'utilisateur avec une interface qui le croit encore connecté.
    vi.mocked(authService.logout).mockRejectedValue(new Error("réseau indisponible"));

    const magasin = useAuthStore();
    magasin.accessToken = "jeton-abc";
    magasin.user = UTILISATEUR;

    await expect(magasin.logout()).rejects.toThrow();
    expect(magasin.accessToken).toBeNull();
    expect(magasin.user).toBeNull();
  });
});

describe("renouvellement de session", () => {
  it("reconstruit la session à partir du cookie", async () => {
    vi.mocked(authService.refresh).mockResolvedValue({ access_token: "jeton-neuf" } as never);
    vi.mocked(authService.me).mockResolvedValue(UTILISATEUR as never);

    const magasin = useAuthStore();
    const reussi = await magasin.tryRefresh();

    expect(reussi).toBe(true);
    expect(magasin.accessToken).toBe("jeton-neuf");
    expect(magasin.user).toEqual(UTILISATEUR);
  });

  it("laisse un état propre quand le cookie n'est plus valide", async () => {
    vi.mocked(authService.refresh).mockRejectedValue(new Error("401"));

    const magasin = useAuthStore();
    magasin.accessToken = "ancien-jeton";
    magasin.user = UTILISATEUR;

    const reussi = await magasin.tryRefresh();

    expect(reussi).toBe(false);
    expect(magasin.accessToken).toBeNull();
    expect(magasin.user).toBeNull();
  });

  it("laisse un état propre si l'identité ne peut pas être relue", async () => {
    // Cas intermédiaire : le jeton est renouvelé mais /auth/me échoue. Sans
    // le rattrapage, la session resterait avec un jeton et sans identité.
    vi.mocked(authService.refresh).mockResolvedValue({ access_token: "jeton-neuf" } as never);
    vi.mocked(authService.me).mockRejectedValue(new Error("500"));

    const magasin = useAuthStore();
    const reussi = await magasin.tryRefresh();

    expect(reussi).toBe(false);
    expect(magasin.accessToken).toBeNull();
    expect(magasin.user).toBeNull();
  });

  it("marque l'initialisation faite, que le renouvellement réussisse ou non", async () => {
    vi.mocked(authService.refresh).mockRejectedValue(new Error("401"));

    const magasin = useAuthStore();
    await magasin.initialize();

    expect(magasin.isInitialized).toBe(true);
    expect(magasin.isAuthenticated).toBe(false);
  });
});
