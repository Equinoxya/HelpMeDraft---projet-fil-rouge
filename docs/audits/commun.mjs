/**
 * Outillage partagé par les scripts d'audit de ce dossier.
 *
 * Il existe parce que `audit-accessibilite.mjs` et `tests-systeme.mjs`
 * faisaient les mêmes trois choses chacun de son côté : lancer Chromium,
 * ouvrir une session authentifiée, et juger si la prise de focus est visible.
 * SonarCloud l'a relevé — 11,6 % de duplication sur le code ajouté — et il
 * avait raison : la règle « le contour peut être porté par un ascendant » est
 * un raisonnement, pas un détail de script, et elle n'a pas à être écrite deux
 * fois.
 */
import { chromium } from "playwright";

export const FRONT = process.env.FRONT_URL || "http://localhost:8080";
export const API = process.env.API_URL || "http://localhost:5000";

/**
 * Mot de passe des comptes du jeu d'essai.
 *
 * Il n'est PAS écrit ici. Non pas qu'il soit secret — `database/jeu_essai.py`
 * l'affiche en clair à la fin de son chargement, et il ne vaut que pour une
 * base de test — mais un mot de passe en dur dans un fichier versionné est un
 * constat de sécurité que les analyseurs remontent à juste titre, et qu'on ne
 * veut pas apprendre à ignorer.
 */
export function motDePasseJeuEssai() {
  const mdp = process.env.MDP_JEU_ESSAI;
  if (!mdp) {
    throw new Error(
      "MDP_JEU_ESSAI est requis. C'est le mot de passe commun aux comptes du jeu " +
        "d'essai, affiché par « python -m database.jeu_essai » à la fin de son " +
        "chargement (constante MDP_JEU_ESSAI de database/jeu_essai.py).",
    );
  }
  return mdp;
}

/**
 * CHROMIUM_PATH permet de pointer un Chromium déjà présent sur la machine,
 * quand le numéro de build attendu par Playwright n'y est pas — c'est le cas
 * des conteneurs qui embarquent leur propre navigateur. Sans cette variable,
 * Playwright utilise celui qu'il a téléchargé.
 */
export function lancerNavigateur() {
  return chromium.launch(
    process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {},
  );
}

export async function nouvelOnglet(navigateur) {
  const ctx = await navigateur.newContext({ viewport: { width: 1280, height: 900 } });
  return { ctx, page: await ctx.newPage() };
}

/**
 * Ouvre une session par l'interface, et non par l'API : c'est le parcours réel,
 * cookie de rafraîchissement compris.
 *
 * `/auth/login` est limité à 5 requêtes par minute ET PAR WORKER (Flask-Limiter
 * compte en mémoire). Une campagne de tests épuise donc le seuil : on attend la
 * fenêtre suivante plutôt que de conclure à un échec de connexion.
 */
export async function connecter(page, email, mdp = motDePasseJeuEssai()) {
  for (const essai of [1, 2]) {
    await page.goto(`${FRONT}/login`, { waitUntil: "networkidle" });
    await page.fill('input[type="email"]', email);
    await page.fill('input[type="password"]', mdp);
    await page.click('button[type="submit"]');
    try {
      await page.waitForURL("**/dashboard", { timeout: 15000 });
      return;
    } catch (e) {
      if (essai === 2) throw e;
      const message = ((await page.textContent("main").catch(() => "")) || "").slice(0, 120);
      console.log(`     (connexion refusée — « ${message.replace(/\s+/g, " ").trim()} »`);
      console.log(`      attente de la fenêtre de limitation de débit…)`);
      await page.waitForTimeout(62000);
    }
  }
}

/**
 * Évalué DANS la page : l'élément focalisé montre-t-il une indication ?
 *
 * On remonte la chaîne des ascendants, parce qu'un contour peut être porté par
 * un parent — c'est le cas de CodeMirror, qui focalise `.cm-content` et dessine
 * le contour sur `.cm-editor`. Le mesurer sur le seul élément actif produirait
 * un faux positif.
 *
 * L'appelant doit laisser les transitions finir avant d'appeler : un
 * `transition: all` fait monter outline-width de 0 à sa valeur finale, et une
 * mesure prise à l'instant du Tab conclut à tort à l'absence de contour.
 */
export const MESURE_FOCUS = () => {
  const indique = (el) => {
    for (let n = el; n && n !== document.body; n = n.parentElement) {
      const s = getComputedStyle(n);
      if (s.outlineStyle !== "none" && parseFloat(s.outlineWidth) > 0) return true;
      if (s.boxShadow && s.boxShadow !== "none") return true;
    }
    return false;
  };
  const el = document.activeElement;
  if (!el || el === document.body) return null;
  return {
    balise: el.tagName.toLowerCase(),
    texte: (el.textContent || "").trim().slice(0, 30) || el.getAttribute("aria-label") || "",
    focusVisible: indique(el),
  };
};

/** Délai laissé aux transitions CSS avant de lire l'état de focus. */
export const ATTENTE_TRANSITION_MS = 250;

/**
 * Ouvre une session par l'API et renvoie les en-têtes à réutiliser.
 *
 * Les trois tests qui passent par l'API refaisaient cette séquence chacun de son
 * côté — c'est la part de duplication que SonarCloud relevait encore après la
 * première mise en commun.
 */
export async function entetesApi(email, mdp = motDePasseJeuEssai()) {
  const r = await fetch(`${API}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, mdp }),
  });
  const { access_token: jeton } = await r.json();
  if (!jeton) throw new Error(`connexion refusée pour ${email} (HTTP ${r.status})`);
  return { "Content-Type": "application/json", Authorization: `Bearer ${jeton}` };
}

/** Identifiant du premier document du compte — les tests n'ont besoin que d'un. */
export async function premierDocument(entetes) {
  const liste = await (await fetch(`${API}/documents`, { headers: entetes })).json();
  return liste.items[0]?.id_document;
}

/** Demande une génération IA sur un document, et renvoie le code et le corps. */
export async function demanderGeneration(entetes, idDocument) {
  const reponse = await fetch(`${API}/documents/${idDocument}/ia/generer`, {
    method: "POST",
    headers: entetes,
    body: JSON.stringify({
      type_action: "corriger",
      scope: "document",
      contenu: "Un text fautif.",
    }),
  });
  return { code: reponse.status, corps: await reponse.json() };
}
