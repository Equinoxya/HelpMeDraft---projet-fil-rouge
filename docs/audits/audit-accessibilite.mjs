/**
 * Rejoue l'audit d'accessibilité de HelpMeDraft après les correctifs du §9.
 *
 * Même méthode que l'audit du 03/10/2026 : axe-core piloté par Playwright sur
 * chaque écran, en deux contextes (anonyme pour les écrans publics et invité,
 * authentifié pour le reste), plus les contrôles manuels qu'axe ne fait pas —
 * titre de page, lien d'évitement, repères, sauts de niveau de titre, taille
 * des cibles et visibilité du focus.
 *
 * Prérequis — Playwright et axe-core ne sont PAS des dépendances du projet : ce
 * script est un outil d'audit, pas du code livré, et les faire entrer dans
 * `frontend/package.json` alourdirait l'installation de tout le monde pour un
 * usage ponctuel.
 *
 *   npm install playwright axe-core        # dans un dossier à part
 *   npx playwright install chromium        # ou CHROMIUM_PATH=/chemin/vers/chrome
 *
 * Puis, l'application démarrée. Deux façons, l'une et l'autre vérifiées :
 *
 *   • sur la pile conteneurisée, qui audite le bundle tel que nginx le sert :
 *       docker compose up --build -d
 *       BASE_URL=http://localhost:8080
 *
 *   • ou sur un lancement local, en servant le frontend CONSTRUIT (et non le
 *     serveur de développement, dont le code n'est pas celui qui est livré) :
 *       JWT_SECRET_KEY=… SECRET_KEY=… HELPMEDRAFT_DB_URL=sqlite:///… \
 *         CORS_ORIGINS=http://localhost:4173 python run.py
 *       VITE_API_URL=http://localhost:5000 npm run build && npx vite preview --port 4173
 *
 * Enfin, un compte créé via POST /auth/register et promu `admin` en base pour
 * atteindre le back-office (E16), puis :
 *
 *   COMPTE_AUDIT_MDP=<son mot de passe> node audit-accessibilite.mjs
 *
 * Variables lues : BASE_URL, COMPTE_AUDIT_EMAIL, COMPTE_AUDIT_MDP (requise),
 * CHROMIUM_PATH. Le résultat est écrit dans resultat-a11y.json, à verser ici
 * sous accessibilite-AAAA-MM-JJ.json.
 */
import { readFileSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import {
  ATTENTE_TRANSITION_MS,
  MESURE_FOCUS,
  lancerNavigateur,
  nouvelOnglet,
} from "./commun.mjs";

const require = createRequire(import.meta.url);
const AXE = readFileSync(require.resolve("axe-core/axe.min.js"), "utf8");

// L'audit tourne contre le frontend CONSTRUIT (vite preview, port 4173) et non
// le serveur de développement : c'est le bundle livré qu'on audite.
const BASE = process.env.BASE_URL || "http://localhost:4173";

// Compte dédié à l'audit, créé par l'opérateur avant de lancer le script (voir
// les prérequis en tête de fichier). Le mot de passe vient de l'environnement :
// un identifiant en dur dans un fichier versionné est un constat de sécurité,
// même sur un compte de test.
const COMPTE = {
  email: process.env.COMPTE_AUDIT_EMAIL || "audit.a11y@exemple.fr",
  mdp: process.env.COMPTE_AUDIT_MDP,
};
if (!COMPTE.mdp) {
  throw new Error(
    "COMPTE_AUDIT_MDP est requis : mot de passe du compte créé pour l'audit " +
      `(${COMPTE.email}). Voir les prérequis en tête de ce fichier.`,
  );
}

const ECRANS = [
  { id: "E01", nom: "Accueil", url: "/", auth: false },
  { id: "E02", nom: "Fonctionnalités", url: "/fonctionnalites", auth: false },
  { id: "E03", nom: "Tarifs", url: "/tarifs", auth: false },
  { id: "E04", nom: "Modèles", url: "/modeles", auth: false },
  { id: "E05", nom: "Mentions légales", url: "/mentions-legales", auth: false },
  { id: "E06", nom: "CGU", url: "/cgu", auth: false },
  { id: "E07", nom: "Confidentialité", url: "/confidentialite", auth: false },
  { id: "E08", nom: "Connexion", url: "/login", auth: false },
  { id: "E09", nom: "Inscription", url: "/register", auth: false },
  { id: "E10", nom: "Mot de passe oublié", url: "/forgot-password", auth: false },
  { id: "E11", nom: "Nouveau mot de passe", url: "/reset-password?token=factice", auth: false },
  { id: "E12", nom: "Tableau de bord", url: "/dashboard", auth: true },
  { id: "E13", nom: "Mes documents", url: "/documents", auth: true },
  { id: "E14", nom: "Nouveau document", url: "/documents/nouveau", auth: true },
  { id: "E16", nom: "Back-office", url: "/admin", auth: true },
];

/** Contrôles manuels, exécutés dans la page. */
const MESURES = () => {
  const visible = (el) => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return (
      r.width > 0 && r.height > 0 && s.visibility !== "hidden" && s.display !== "none"
    );
  };

  // Sauts de niveau : un titre ne doit pas descendre de plus d'un cran.
  const titres = [...document.querySelectorAll("h1,h2,h3,h4,h5,h6")].filter(visible);
  const sauts = [];
  let precedent = 0;
  for (const t of titres) {
    const niveau = Number(t.tagName[1]);
    if (precedent && niveau > precedent + 1) {
      sauts.push(`h${precedent} → h${niveau} (« ${t.textContent.trim().slice(0, 40)} »)`);
    }
    precedent = niveau;
  }

  // Lien d'évitement : premier élément focalisable, pointant vers un ancrage
  // présent dans la page.
  const focalisables = [
    ...document.querySelectorAll(
      'a[href], button, input, select, textarea, [tabindex]:not([tabindex="-1"])',
    ),
  ];
  const premier = focalisables[0];
  const cible = premier?.getAttribute("href")?.startsWith("#")
    ? document.querySelector(premier.getAttribute("href"))
    : null;

  // Taille de cible — WCAG 2.2 · 2.5.8 (24 × 24 px). Un lien en ligne dans un
  // bloc de texte bénéficie d'une exception : on le signale à part plutôt que
  // de le compter comme non conforme.
  const enLigneDansDuTexte = (el) => {
    if (getComputedStyle(el).display !== "inline") return false;
    const parent = el.parentElement;
    if (!parent) return false;
    const texteParent = parent.textContent.trim().length;
    return texteParent > el.textContent.trim().length + 20;
  };

  // Un élément en sr-only est réduit à 1 px et déplacé hors écran : il n'est
  // une cible qu'une fois focalisé (c'est le cas du lien d'évitement, mesuré à
  // part dans le parcours clavier). Le compter ici serait un faux positif.
  const masquePourLesYeux = (el) => {
    const s = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    return (s.clip !== "auto" || s.clipPath !== "none") && r.width <= 2 && r.height <= 2;
  };

  const petites = [];
  const petitesEnLigne = [];
  for (const el of focalisables) {
    if (!visible(el)) continue;
    if (masquePourLesYeux(el)) continue;
    const r = el.getBoundingClientRect();
    if (r.width >= 24 && r.height >= 24) continue;
    const entree = {
      balise: el.tagName.toLowerCase(),
      l: Math.round(r.width),
      h: Math.round(r.height),
      texte: el.textContent.trim().slice(0, 40) || el.getAttribute("aria-label") || "",
    };
    (enLigneDansDuTexte(el) ? petitesEnLigne : petites).push(entree);
  }

  return {
    titre: document.title,
    langue: document.documentElement.lang,
    h1: document.querySelectorAll("h1").length,
    titres: titres.length,
    sautsDeNiveau: sauts,
    lienEvitement: Boolean(cible),
    lienEvitementTexte: cible ? premier.textContent.trim() : null,
    reperes: {
      main: document.querySelectorAll("main").length,
      nav: document.querySelectorAll("nav").length,
      header: document.querySelectorAll("header").length,
      footer: document.querySelectorAll("footer").length,
    },
    interactifs: focalisables.filter(visible).length,
    ciblesTropPetites: petites,
    ciblesEnLigneExemptees: petitesEnLigne,
  };
};

const navigateur = await lancerNavigateur();

async function contexte(authentifie) {
  const { ctx, page } = await nouvelOnglet(navigateur);
  if (authentifie) {
    await page.goto(`${BASE}/login`, { waitUntil: "networkidle" });
    await page.fill('input[type="email"]', COMPTE.email);
    await page.fill('input[type="password"]', COMPTE.mdp);
    await page.click('button[type="submit"]');
    await page.waitForURL("**/dashboard", { timeout: 15000 });
  }
  return { ctx, page };
}

const resultats = [];
let violationsTotales = 0;

for (const authentifie of [false, true]) {
  const ecrans = ECRANS.filter((e) => e.auth === authentifie);
  const { ctx, page } = await contexte(authentifie);

  for (const ecran of ecrans) {
    await page.goto(BASE + ecran.url, { waitUntil: "networkidle" });
    await page.waitForTimeout(400);

    await page.addScriptTag({ content: AXE });
    const axeResultat = await page.evaluate(async () => {
      // eslint-disable-next-line no-undef
      const r = await axe.run(document, {
        runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"] },
      });
      return r.violations.map((v) => ({
        id: v.id,
        impact: v.impact,
        occurrences: v.nodes.length,
        cibles: v.nodes.slice(0, 3).map((n) => n.target.join(" ")),
      }));
    });

    const mesures = await page.evaluate(MESURES);

    // Taille du lien d'évitement une fois focalisé — le seul état où il est une cible.
    await page.keyboard.press("Tab");
    await page.waitForTimeout(ATTENTE_TRANSITION_MS);
    mesures.lienEvitementFocalise = await page.evaluate(() => {
      const el = document.activeElement;
      const r = el.getBoundingClientRect();
      return { texte: el.textContent.trim(), l: Math.round(r.width), h: Math.round(r.height) };
    });

    // Parcours clavier
    const clavier = { atteints: 0, sansFocusVisible: 0, exemplesSansFocus: [] };
    await page.evaluate(() => document.body.focus());
    for (let i = 0; i < 40; i++) {
      await page.keyboard.press("Tab");
      await page.waitForTimeout(ATTENTE_TRANSITION_MS);
      const actif = await page.evaluate(MESURE_FOCUS);
      if (!actif) continue;
      clavier.atteints++;
      if (!actif.focusVisible) {
        clavier.sansFocusVisible++;
        if (clavier.exemplesSansFocus.length < 5) clavier.exemplesSansFocus.push(actif);
      }
    }

    violationsTotales += axeResultat.reduce((n, v) => n + v.occurrences, 0);
    resultats.push({ ...ecran, axe: axeResultat, ...mesures, clavier });
    const ko =
      axeResultat.length ||
      mesures.sautsDeNiveau.length ||
      !mesures.lienEvitement ||
      !mesures.h1 ||
      !mesures.reperes.main ||
      mesures.ciblesTropPetites.length ||
      clavier.sansFocusVisible;
    console.log(
      `${ecran.id} ${ecran.nom.padEnd(22)} axe=${axeResultat.length} sauts=${mesures.sautsDeNiveau.length} ` +
        `evit=${mesures.lienEvitement ? "oui" : "NON"} main=${mesures.reperes.main} h1=${mesures.h1} ` +
        `cibles<24=${mesures.ciblesTropPetites.length} (+${mesures.ciblesEnLigneExemptees.length} exemptées) ` +
        `focusKO=${clavier.sansFocusVisible} titre="${mesures.titre}" ${ko ? "⚠" : "✔"}`,
    );
  }
  await ctx.close();
}

await navigateur.close();
writeFileSync(
  new URL("./resultat-a11y.json", import.meta.url),
  JSON.stringify({ date: new Date().toISOString(), base: BASE, ecrans: resultats }, null, 2),
);
console.log(`\nTotal violations axe-core : ${violationsTotales}`);
