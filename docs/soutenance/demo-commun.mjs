/**
 * Captation vidéo — rouages communs aux démonstrations
 *
 * Pilote un Chromium réel sur l'application en fonctionnement et enregistre
 * le parcours. Les sous-titres sont incrustés dans la page (overlay DOM),
 * donc gravés dans la vidéo : rien à monter après coup.
 *
 * Deux scénarios s'en servent : enregistrer-demo.mjs (la version courte,
 * intégrée au diaporama) et demo-3min.mjs (la version longue, livrée à part).
 *
 * PRÉREQUIS
 *   1. backend  : cd backend && python run.py                   (port 5000)
 *   2. frontend : cd frontend && npm run dev                    (port 5173)
 *   3. base     : cd backend && python database/jeu_essai.py --vider
 *   4. Ollama   : ollama serve + ollama pull qwen2.5:3b          (port 11434)
 *
 * Sans Ollama, la séquence IA échoue en 502 et le script le signale à l'écran
 * au lieu de s'arrêter — la vidéo reste exploitable, mais la génération n'y
 * figure pas.
 *
 * Ce fichier n'enregistre rien par lui-même : il expose les rouages, et
 * `executer()` déroule le scénario que le script appelant lui passe.
 */

import { mkdirSync, readdirSync, renameSync } from "node:fs";
import { join, resolve } from "node:path";
import { createRequire } from "node:module";

// Playwright peut être installé dans le projet ou globalement. L'import ESM
// n'honore pas NODE_PATH : on passe par createRequire, qui le trouve dans les
// deux cas.
const exiger = createRequire(import.meta.url);
let chromium;
try {
  ({ chromium } = await import("playwright"));
} catch {
  ({ chromium } = exiger("playwright"));
}

export const BASE = process.env.DEMO_URL ?? "http://localhost:5173";
export const MDP = process.env.DEMO_MDP ?? "JeuDEssai1";

/**
 * Vrai si un VRAI Ollama répond. Sinon la captation reste possible avec un
 * substitut, mais la vidéo DOIT le dire : une démonstration qui laisse croire
 * qu'un modèle a tourné alors qu'il n'y en a pas est une démonstration fausse.
 */
export const OLLAMA_REEL = await fetch(`${process.env.OLLAMA_URL ?? "http://127.0.0.1:11434"}/api/version`)
  .then((r) => r.ok)
  .catch(() => false);

export const COMPTES = {
  camille: "camille@helpmedraft.test",
  karim: "karim@helpmedraft.test",
  admin: "admin@helpmedraft.test",
};

export const pause = (ms) => new Promise((r) => setTimeout(r, ms));

// Les appels d'API faits DEPUIS la page passent par le proxy /api de Vite, et
// non par le port 5000 en direct. Le backend pose le cookie de refresh sur
// « Path=/auth » ; le proxy le réécrit en « /api/auth » (cookiePathRewrite dans
// vite.config.ts). Visée directement, la racine du backend ne reçoit donc
// jamais le cookie : /auth/refresh répond 401 et toute la démonstration
// d'API s'effondre en affichant 401 là où elle devrait montrer 429 ou 404.
export const API = process.env.DEMO_API ?? `${BASE}/api`;

/**
 * Le jeton d'accès vit en mémoire dans le store Pinia, jamais dans
 * localStorage — c'est voulu. Pour interroger l'API depuis la page, on
 * repasse donc par le cookie de refresh, httpOnly, que le navigateur joint
 * tout seul.
 */
export async function appelApi(page, chemin, options = {}) {
  return page.evaluate(
    async ([api, chemin, options]) => {
      const r0 = await fetch(`${api}/auth/refresh`, { method: "POST", credentials: "include" });
      if (!r0.ok) return { statut: r0.status, corps: "refresh refusé" };
      const { access_token } = await r0.json();
      const r = await fetch(`${api}${chemin}`, {
        method: options.method ?? "GET",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${access_token}` },
        body: options.body ? JSON.stringify(options.body) : undefined,
      });
      let corps;
      try { corps = await r.json(); } catch { corps = null; }
      return { statut: r.status, corps };
    },
    [API, chemin, options],
  );
}


// ─────────────────────────── sous-titres ───────────────────────────

const OVERLAY = `
(() => {
  if (document.getElementById('__demo_overlay')) return;
  const barre = document.createElement('div');
  barre.id = '__demo_overlay';
  barre.style.cssText = [
    'position:fixed','left:0','right:0','bottom:0','z-index:2147483647',
    'background:#111111','color:#F4F1EA','padding:14px 28px',
    'font:600 19px/1.45 Georgia,serif','letter-spacing:.2px',
    'border-top:4px solid #E0533C','pointer-events:none',
    'transition:opacity .25s','opacity:0','min-height:30px',
  ].join(';');
  const puce = document.createElement('span');
  puce.id = '__demo_puce';
  puce.style.cssText = 'color:#E0533C;font:700 12px/1 "Courier New",monospace;letter-spacing:2px;text-transform:uppercase;display:block;margin-bottom:5px';
  const texte = document.createElement('span');
  texte.id = '__demo_texte';
  barre.append(puce, texte);
  document.body.appendChild(barre);
})();`;

export async function soustitre(page, surtitre, texte) {
  await page.evaluate(OVERLAY).catch(() => {});
  await page
    .evaluate(
      ([s, t]) => {
        const barre = document.getElementById("__demo_overlay");
        if (!barre) return;
        document.getElementById("__demo_puce").textContent = s;
        document.getElementById("__demo_texte").textContent = t;
        barre.style.opacity = t ? "1" : "0";
      },
      [surtitre, texte],
    )
    .catch(() => {});
}

/** Carte pleine page, pour l'ouverture et la clôture. */
export async function carte(page, titre, lignes, sousTitre = "") {
  await page.evaluate(
    ([titre, lignes, sousTitre]) => {
      const vue = document.createElement("div");
      vue.id = "__demo_carte";
      vue.style.cssText = [
        "position:fixed","inset:0","z-index:2147483646","background:#111111",
        "color:#F4F1EA","display:flex","flex-direction:column",
        "justify-content:center","padding:0 10vw","font-family:Georgia,serif",
      ].join(";");
      const st = document.createElement("div");
      st.textContent = sousTitre;
      st.style.cssText = 'color:#E0533C;font:700 14px/1 "Courier New",monospace;letter-spacing:3px;text-transform:uppercase;margin-bottom:22px';
      const h = document.createElement("div");
      h.textContent = titre;
      h.style.cssText = "font-size:54px;font-weight:700;line-height:1.1;margin-bottom:28px";
      const ul = document.createElement("div");
      ul.style.cssText = "font-size:22px;line-height:1.75;max-width:62ch";
      for (const l of lignes) {
        const p = document.createElement("div");
        p.textContent = l;
        p.style.cssText = "margin-bottom:9px";
        ul.appendChild(p);
      }
      vue.append(st, h, ul);
      document.body.appendChild(vue);
    },
    [titre, lignes, sousTitre],
  );
}

export const retirerCarte = (page) =>
  page.evaluate(() => document.getElementById("__demo_carte")?.remove()).catch(() => {});

/** Frappe lisible à l'écran : ni instantanée, ni interminable. */
export const frapper = (cible, texte, delay = 55) => cible.pressSequentially(texte, { delay });

/**
 * Saisie dans CodeMirror. `type()` y réordonne des caractères sous charge
 * (constaté : « rien recu » devenait « ien recur »). insertText mot à mot
 * conserve l'effet de frappe sans les fautes.
 */
export async function frapperEditeur(page, cible, texte, delai = 110) {
  await cible.click();
  for (const mot of texte.split(/(?<=\s)/)) {
    await page.keyboard.insertText(mot);
    await pause(delai);
  }
}

export async function connexion(page, compte) {
  await page.goto(`${BASE}/login`, { waitUntil: "networkidle" });
  await page.fill("#email", COMPTES[compte] ?? compte);
  await page.fill("#mdp", MDP);
  await pause(500);
  await page.getByRole("button", { name: /se connecter|connexion/i }).first().click();
  await page.waitForURL(/dashboard|admin/, { timeout: 15000 }).catch(() => {});
  await pause(1200);
}

export async function deconnexion(page) {
  // On clique le VRAI bouton. Appeler /auth/logout depuis la page ne marche
  // pas : le front passe par le proxy /api de Vite, qui réécrit le chemin du
  // cookie de refresh. Visé directement sur le port 5000, le cookie n'est pas
  // joint, le serveur ne révoque rien, et la session suivante reste ouverte.
  const bouton = page.getByRole("button", { name: /déconnexion|se déconnecter/i }).first();
  if (await bouton.isVisible().catch(() => false)) {
    await bouton.click().catch(() => {});
    await page.waitForURL(/login|\/$/, { timeout: 8000 }).catch(() => {});
  } else {
    await page.evaluate(
      (api) => fetch(`${api}/auth/logout`, { method: "POST", credentials: "include" }).catch(() => {}),
      API,
    );
  }
  await page.goto(`${BASE}/login`, { waitUntil: "networkidle" }).catch(() => {});
  // Si la session a survécu, le routeur renvoie vers le tableau de bord : on
  // le dit plutôt que d'échouer trente secondes plus loin sur un champ absent.
  if (!/\/login/.test(page.url())) console.warn("    ⚠ session encore ouverte après déconnexion");
  await pause(600);
}


// ─────────────────────────── scénario ───────────────────────────

/** Fabrique un recueil d'étapes : `etape(titre, fn)` les empile dans l'ordre. */
export function scenario() {
  const etapes = [];
  return { etapes, etape: (titre, fn) => etapes.push({ titre, fn }) };
}

// ─────────────────────────── exécution ───────────────────────────

/**
 * Déroule les étapes dans un Chromium enregistré, et renomme la vidéo.
 * Une étape qui échoue est signalée et capturée en image, sans interrompre
 * le reste : une captation partielle vaut mieux qu'aucune.
 */
export async function executer(etapes, { sortie, nom }) {
  mkdirSync(sortie, { recursive: true });

  const navigateur = await chromium.launch({ args: ["--no-sandbox", "--force-device-scale-factor=1"] });
  const contexte = await navigateur.newContext({
    viewport: { width: 1440, height: 900 },
    recordVideo: { dir: sortie, size: { width: 1440, height: 900 } },
    locale: "fr-FR",
    timezoneId: "Europe/Paris",
    reducedMotion: "no-preference",
  });

  // Masque le curseur de saisie clignotant, qui scintille à l'encodage.
  await contexte.addInitScript(() => {
    const style = document.createElement("style");
    style.textContent = "*{caret-color:#C4341C!important}";
    document.documentElement.appendChild(style);
  });

  const page = await contexte.newPage();
  const debutTotal = Date.now();
  let rang = 0;
  for (const { titre, fn } of etapes) {
    rang += 1;
    const debut = Date.now();
    process.stdout.write(`  ${String(rang).padStart(2, "0")}. ${titre}… `);
    try {
      await fn(page);
      console.log(`ok (${((Date.now() - debut) / 1000).toFixed(1)} s)`);
    } catch (erreur) {
      console.log(`ÉCHEC — ${erreur.message.split("\n")[0]}`);
      await page.screenshot({ path: join(sortie, `echec-${rang}-${titre.replace(/\W+/g, "-")}.png`) }).catch(() => {});
    }
  }
  const duree = (Date.now() - debutTotal) / 1000;

  await contexte.close();
  await navigateur.close();

  const brut = readdirSync(sortie).find((f) => f.endsWith(".webm") && !f.startsWith(nom));
  if (brut) renameSync(join(sortie, brut), join(sortie, `${nom}.webm`));
  console.log(`\nDurée captée : ${Math.floor(duree / 60)} min ${String(Math.round(duree % 60)).padStart(2, "0")} s`);
  console.log(`Vidéo : ${join(sortie, `${nom}.webm`)}`);
  return { duree, webm: join(sortie, `${nom}.webm`) };
}
