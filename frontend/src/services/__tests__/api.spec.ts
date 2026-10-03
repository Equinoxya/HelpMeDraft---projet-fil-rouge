/**
 * Tests des intercepteurs du client HTTP — TU-F04 à TU-F07.
 *
 * C'est le mécanisme le plus subtil du frontend, et celui dont une
 * régression se voit le moins à la relecture : le renouvellement du jeton
 * sur 401, et surtout sa mutualisation entre requêtes concurrentes.
 *
 * MÉTHODE — l'adaptateur d'axios est remplacé, pas le module axios. Les
 * intercepteurs s'exécutent donc réellement, seul le transport est simulé.
 * Mocker axios entier ne testerait plus rien.
 */
import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../authService", () => ({
  default: {
    refresh: vi.fn(),
    me: vi.fn(),
    login: vi.fn(),
    logout: vi.fn(),
  },
}));

vi.mock("../../index.ts", () => ({
  default: { push: vi.fn() },
}));

import router from "../../index.ts";
import { useAuthStore } from "../../stores/auth";
import api from "../api";
import authService from "../authService";

type ConfigAxios = { url?: string; headers: Record<string, string>; _retry?: boolean };

/** Journal des requêtes réellement parties, intercepteurs appliqués. */
let requetes: ConfigAxios[] = [];

/**
 * Installe un adaptateur qui répond 401 tant que `jetonAttendu` n'est pas
 * présenté, puis 200. C'est le comportement d'un serveur dont l'access token
 * a expiré.
 */
function adaptateurQuiExige(jetonAttendu: string) {
  api.defaults.adapter = (async (config: ConfigAxios) => {
    requetes.push(config);
    const autorisation = config.headers?.Authorization;
    if (autorisation === `Bearer ${jetonAttendu}`) {
      return { data: { ok: true }, status: 200, statusText: "OK", headers: {}, config };
    }
    return Promise.reject({ response: { status: 401 }, config });
  }) as never;
}

beforeEach(() => {
  setActivePinia(createPinia());
  requetes = [];
  vi.clearAllMocks();
  delete api.defaults.adapter;
});

describe("intercepteur de requête", () => {
  it("TU-F04 · ajoute l'en-tête Authorization quand un jeton est en mémoire", async () => {
    useAuthStore().accessToken = "jeton-valide";
    adaptateurQuiExige("jeton-valide");

    await api.get("/documents");

    expect(requetes[0].headers.Authorization).toBe("Bearer jeton-valide");
  });

  it("n'ajoute aucun en-tête quand la session est vide", async () => {
    api.defaults.adapter = (async (config: ConfigAxios) => {
      requetes.push(config);
      return { data: {}, status: 200, statusText: "OK", headers: {}, config };
    }) as never;

    await api.get("/documents");

    expect(requetes[0].headers.Authorization).toBeUndefined();
  });
});

describe("intercepteur de réponse", () => {
  it("TU-F05 · renouvelle le jeton sur 401 puis rejoue la requête", async () => {
    const magasin = useAuthStore();
    magasin.accessToken = "jeton-perime";
    adaptateurQuiExige("jeton-neuf");

    vi.mocked(authService.refresh).mockResolvedValue({ access_token: "jeton-neuf" } as never);
    vi.mocked(authService.me).mockResolvedValue({
      id: "1", email: "camille@exemple.fr", firstname: "Camille",
      lastname: "Dupont", role: "user",
    } as never);

    const reponse = await api.get("/documents");

    expect(reponse.status).toBe(200);
    expect(authService.refresh).toHaveBeenCalledTimes(1);
    expect(requetes).toHaveLength(2);
    expect(requetes[1].headers.Authorization).toBe("Bearer jeton-neuf");
  });

  it("TU-F06 · mutualise le renouvellement entre requêtes concurrentes", async () => {
    /**
     * Le test qui justifie l'existence de ce fichier.
     *
     * Sans mutualisation, trois 401 simultanés déclenchent trois appels à
     * /auth/refresh. Or chaque rotation invalide le jeton précédent et le
     * serveur traite un jeton déjà tourné comme un rejeu : il coupe toutes
     * les sessions du compte. L'utilisateur serait déconnecté précisément
     * parce que son application a bien fonctionné.
     */
    const magasin = useAuthStore();
    magasin.accessToken = "jeton-perime";
    adaptateurQuiExige("jeton-neuf");

    let renouvellements = 0;
    vi.mocked(authService.refresh).mockImplementation(async () => {
      renouvellements += 1;
      await new Promise((r) => setTimeout(r, 10)); // le renouvellement n'est pas instantané
      return { access_token: "jeton-neuf" } as never;
    });
    vi.mocked(authService.me).mockResolvedValue({ id: "1", role: "user" } as never);

    const reponses = await Promise.all([
      api.get("/documents"),
      api.get("/dossiers"),
      api.get("/auth/me"),
    ]);

    expect(reponses.every((r) => r.status === 200)).toBe(true);
    expect(renouvellements).toBe(1);
    expect(requetes).toHaveLength(6); // 3 échecs, puis 3 rejeux
  });

  it("TU-F07 · ne boucle pas quand le renouvellement échoue, et renvoie à la connexion", async () => {
    const magasin = useAuthStore();
    magasin.accessToken = "jeton-perime";
    adaptateurQuiExige("jeton-inatteignable");

    vi.mocked(authService.refresh).mockRejectedValue(new Error("session expirée"));

    await expect(api.get("/documents")).rejects.toBeTruthy();

    expect(magasin.accessToken).toBeNull();
    expect(router.push).toHaveBeenCalledWith({ name: "login" });
    expect(requetes).toHaveLength(1); // aucun rejeu : pas de boucle
  });

  it("ne tente pas de renouvellement quand c'est /auth/refresh qui échoue", async () => {
    useAuthStore().accessToken = "jeton-perime";
    api.defaults.adapter = (async (config: ConfigAxios) => {
      requetes.push(config);
      return Promise.reject({ response: { status: 401 }, config });
    }) as never;

    await expect(api.post("/auth/refresh")).rejects.toBeTruthy();

    expect(authService.refresh).not.toHaveBeenCalled();
    expect(requetes).toHaveLength(1);
  });

  it("laisse passer les erreurs qui ne sont pas des 401", async () => {
    useAuthStore().accessToken = "jeton-valide";
    api.defaults.adapter = (async (config: ConfigAxios) => {
      requetes.push(config);
      return Promise.reject({ response: { status: 500 }, config });
    }) as never;

    await expect(api.get("/documents")).rejects.toBeTruthy();

    expect(authService.refresh).not.toHaveBeenCalled();
    expect(requetes).toHaveLength(1);
  });

  it("transmet le cookie de session sur toutes les requêtes", () => {
    // withCredentials conditionne l'envoi du cookie HttpOnly de
    // rafraîchissement : sans lui, /auth/refresh échouerait toujours.
    expect(api.defaults.withCredentials).toBe(true);
  });
});
