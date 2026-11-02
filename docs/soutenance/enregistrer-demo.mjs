/**
 * Captation vidéo de la démonstration — HelpMeDraft
 *
 * Pilote un Chromium réel sur l'application en fonctionnement et enregistre
 * le parcours. Les sous-titres sont incrustés dans la page (overlay DOM),
 * donc gravés dans la vidéo : rien à monter après coup.
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
 * LANCEMENT
 *   node docs/soutenance/enregistrer-demo.mjs [dossier-de-sortie]
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

const BASE = process.env.DEMO_URL ?? "http://localhost:5173";
const SORTIE = resolve(process.argv[2] ?? "docs/soutenance/demo");
const MDP = process.env.DEMO_MDP ?? "JeuDEssai1";

/**
 * Vrai si un VRAI Ollama répond. Sinon la captation reste possible avec un
 * substitut, mais la vidéo DOIT le dire : une démonstration qui laisse croire
 * qu'un modèle a tourné alors qu'il n'y en a pas est une démonstration fausse.
 */
const OLLAMA_REEL = await fetch(`${process.env.OLLAMA_URL ?? "http://127.0.0.1:11434"}/api/version`)
  .then((r) => r.ok)
  .catch(() => false);

const COMPTES = {
  camille: "camille@helpmedraft.test",
  karim: "karim@helpmedraft.test",
  admin: "admin@helpmedraft.test",
};

const pause = (ms) => new Promise((r) => setTimeout(r, ms));

const API = process.env.DEMO_API ?? "http://localhost:5000";

/**
 * Le jeton d'accès vit en mémoire dans le store Pinia, jamais dans
 * localStorage — c'est voulu. Pour interroger l'API depuis la page, on
 * repasse donc par le cookie de refresh, httpOnly, que le navigateur joint
 * tout seul.
 */
async function appelApi(page, chemin, options = {}) {
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

async function soustitre(page, surtitre, texte) {
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
async function carte(page, titre, lignes, sousTitre = "") {
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

const retirerCarte = (page) =>
  page.evaluate(() => document.getElementById("__demo_carte")?.remove()).catch(() => {});

/** Frappe lisible à l'écran : ni instantanée, ni interminable. */
const frapper = (cible, texte, delay = 55) => cible.pressSequentially(texte, { delay });

/**
 * Saisie dans CodeMirror. `type()` y réordonne des caractères sous charge
 * (constaté : « rien recu » devenait « ien recur »). insertText mot à mot
 * conserve l'effet de frappe sans les fautes.
 */
async function frapperEditeur(page, cible, texte, delai = 110) {
  await cible.click();
  for (const mot of texte.split(/(?<=\s)/)) {
    await page.keyboard.insertText(mot);
    await pause(delai);
  }
}

async function connexion(page, compte) {
  await page.goto(`${BASE}/login`, { waitUntil: "networkidle" });
  await page.fill("#email", COMPTES[compte] ?? compte);
  await page.fill("#mdp", MDP);
  await pause(500);
  await page.getByRole("button", { name: /se connecter|connexion/i }).first().click();
  await page.waitForURL(/dashboard|admin/, { timeout: 15000 }).catch(() => {});
  await pause(1200);
}

async function deconnexion(page) {
  // Le store est en mémoire : un simple rechargement suffirait presque, mais
  // le cookie de refresh relancerait la session. On révoque côté serveur.
  await page.evaluate(
    (api) => fetch(`${api}/auth/logout`, { method: "POST", credentials: "include" }).catch(() => {}),
    API,
  );
  await page.goto(`${BASE}/login`, { waitUntil: "networkidle" }).catch(() => {});
  await pause(600);
}

// ─────────────────────────── scénario ───────────────────────────

const etapes = [];
const etape = (titre, fn) => etapes.push({ titre, fn });

etape("Ouverture", async (page) => {
  await page.goto(BASE, { waitUntil: "networkidle" });
  await carte(
    page,
    "HelpMeDraft",
    [
      "Assistant de rédaction professionnelle assistée par IA.",
      "Le modèle de langage tourne en local : aucun contenu",
      "ne quitte l'infrastructure de l'entreprise.",
      "",
      "Ophélie Bellissens — titre CDA",
    ],
    "Démonstration",
  );
  await pause(5200);
  await retirerCarte(page);
  await soustitre(page, "Page d'accueil", "Le produit et sa promesse : une IA qui ne sort pas de chez vous.");
  await pause(2600);
  await page.mouse.wheel(0, 620);
  await pause(2600);
  await page.mouse.wheel(0, 700);
  await pause(2400);
});

etape("Connexion", async (page) => {
  await page.goto(`${BASE}/login`, { waitUntil: "networkidle" });
  await soustitre(page, "Authentification", "Access token de 15 minutes, refresh token de 7 jours révocable côté serveur.");
  await pause(1800);
  await frapper(page.locator("#email"), COMPTES.camille, 42);
  await pause(350);
  await frapper(page.locator("#mdp"), MDP, 60);
  await pause(900);
  await page.getByRole("button", { name: /se connecter|connexion/i }).first().click();
  await page.waitForURL(/dashboard/, { timeout: 15000 }).catch(() => {});
  await pause(1500);
});

etape("Tableau de bord", async (page) => {
  await soustitre(page, "Tableau de bord", "Les compteurs viennent de l'API, pas d'un calcul côté navigateur.");
  await pause(3200);
  await page.mouse.wheel(0, 420);
  await soustitre(page, "Tableau de bord", "Trois portes d'entrée vers la rédaction : supprimer la page blanche.");
  await pause(3400);
  await page.mouse.wheel(0, -420);
  await pause(900);
});

etape("Liste des documents", async (page) => {
  await page.goto(`${BASE}/documents`, { waitUntil: "networkidle" });
  await soustitre(page, "Mes documents", "Pagination serveur : la liste n'est jamais chargée entièrement.");
  await pause(3600);
});

etape("Éditeur et enregistrement automatique", async (page) => {
  await page.goto(`${BASE}/documents/nouveau`, { waitUntil: "networkidle" });
  await pause(1000);
  await soustitre(page, "Éditeur", "Rien n'est enregistré tant que le titre est vide.");
  await pause(2400);

  const titre = page.locator('input[type="text"]').first();
  await titre.click();
  await frapper(titre, "Relance commande 4812", 60);
  await pause(700);

  await soustitre(page, "Éditeur", "L'enregistrement part 2,5 s après la dernière frappe — et un bouton permet de forcer.");
  // CodeMirror : zone « contenteditable » nommée par aria-label, pas un <textarea>.
  const zone = page.getByRole("textbox", { name: /Éditeur de document/i }).first();
  await frapperEditeur(
    page,
    zone,
    "bjr, jai commandé le 12 octobre la commande 4812 et jai toujours rien recu. pouvez vous me dire ou elle en est svp",
  );
  await pause(4200);
});

etape("Génération IA", async (page) => {
  await soustitre(page, "Assistant IA", "Trois actions, et trois seulement : reformuler, corriger, compléter.");
  await page.locator('button[title="Assistant IA"]').first().click();
  await pause(2200);

  const selAction = page.locator("select").filter({ has: page.locator('option[value="reformuler"]') }).first();
  const selPortee = page.locator("select").filter({ has: page.locator('option[value="selection"]') }).first();
  await selAction.selectOption("reformuler").catch(() => {});
  await pause(700);
  await selPortee.selectOption("document").catch(() => {});
  await pause(1100);

  await soustitre(
    page,
    "Assistant IA",
    "Cinq contrôles serveur avant le modèle : authentification, propriété, validation, quota — puis l'appel.",
  );
  await pause(2600);

  await page.getByRole("button", { name: /^Générer$/ }).first().click();
  await soustitre(
    page,
    OLLAMA_REEL ? "Génération" : "Génération — moteur substitué",
    OLLAMA_REEL
      ? "L'attente est annoncée, et la génération reste annulable."
      : "Parcours applicatif réel ; le modèle, lui, est remplacé pour cet enregistrement (pas d'Ollama sur cette machine).",
  );

  await page
    .getByRole("button", { name: /insérer|remplacer/i })
    .first()
    .waitFor({ timeout: 120000 })
    .catch(async () => {
      await soustitre(page, "Moteur indisponible", "Ollama n'est pas joignable sur cet enregistrement : la génération n'aboutit pas.");
      await pause(4000);
    });
  await pause(2400);

  const remplacer = page.getByRole("button", { name: /remplacer/i }).first();
  if (await remplacer.isVisible().catch(() => false)) {
    await soustitre(page, "Décision", "Rien n'est appliqué automatiquement : c'est l'utilisateur qui insère ou remplace.");
    await pause(3400);
    await remplacer.click();
    await pause(2600);
    await soustitre(page, "Résultat", "Le texte retenu remplace le brouillon. L'original reste dans l'historique.");
    await pause(3000);
  }
});

etape("Traçabilité", async (page) => {
  const bouton = page.getByRole("button", { name: /Passages issus/i }).first();
  if (await bouton.isVisible().catch(() => false)) {
    await soustitre(page, "Traçabilité", "L'historique conserve l'action, l'avant, l'après et le nombre de jetons.");
    await bouton.click();
    await pause(3000);
    await page.mouse.wheel(0, 240);
    await soustitre(page, "Traçabilité", "Cette même table sert trois choses : l'historique, le calcul du quota, la preuve RGPD et AI Act.");
    await pause(4000);
  }
});

etape("Quota serveur", async (page) => {
  await deconnexion(page);
  await soustitre(page, "Quota", "Second compte, dont les 20 appels des dernières 24 heures sont déjà consommés.");
  await pause(1200);
  await connexion(page, "karim");

  // Le quota se démontre sur l'API : c'est là qu'il est appliqué.
  await page.goto(`${BASE}/documents`, { waitUntil: "networkidle" });
  await pause(1600);
  const liste = await appelApi(page, "/documents");
  const id = liste.corps?.items?.[0]?.id_document;
  const reponse = id
    ? await appelApi(page, `/documents/${id}/ia/generer`, {
        method: "POST",
        body: { type_action: "corriger", scope: "document", contenu: "bonjour, merci de votre retour" },
      })
    : { statut: "—", corps: { error: "aucun document" } };

  await carte(
    page,
    `HTTP ${reponse.statut}`,
    [
      String(reponse.corps?.error ?? JSON.stringify(reponse.corps)).slice(0, 160),
      "",
      "Le quota est compté par agrégation sur le journal des appels,",
      "sur une fenêtre glissante de 24 heures — pas un compteur remis",
      "à zéro à minuit, et pas un compteur stocké sur l'utilisateur.",
      "",
      "429 Too Many Requests, et non 403 : « réessayez plus tard »",
      "n'est pas la même information que « vous n'avez pas le droit ».",
    ],
    "Contrôle côté serveur",
  );
  await pause(7500);
  await retirerCarte(page);
});

etape("Cloisonnement", async (page) => {
  const autrui = process.env.DEMO_DOC_AUTRUI ?? "00000000-0000-0000-0000-000000000000";
  const { statut: resultat } = await appelApi(page, `/documents/${autrui}`);
  await carte(
    page,
    `HTTP ${resultat}`,
    [
      "Un document qui n'appartient pas au compte courant",
      "renvoie 404, et non 403.",
      "",
      "La propriété est dans la clause WHERE : la requête demande",
      "un document qui a cet identifiant ET qui appartient à",
      "l'utilisateur. Un 403 confirmerait que la ressource existe.",
    ],
    "Cloisonnement des données",
  );
  await pause(7000);
  await retirerCarte(page);
});

etape("Back-office", async (page) => {
  await deconnexion(page);
  await connexion(page, "admin");
  await page.goto(`${BASE}/admin`, { waitUntil: "networkidle" });
  await soustitre(page, "Back-office", "Statistiques d'usage, recherche de comptes, et journal des actions d'administration.");
  await pause(4000);
  await page.mouse.wheel(0, 500);
  await pause(3600);
  await page.mouse.wheel(0, 600);
  await soustitre(page, "Back-office", "Le rôle est relu en base à chaque requête — jamais lu dans le jeton.");
  await pause(3600);
});

etape("Clôture", async (page) => {
  await soustitre(page, "", "");
  await carte(
    page,
    "Ce que la démonstration montre",
    [
      "· Les contrôles sont côté serveur, pas dans l'interface.",
      "· Le navigateur ne parle jamais au moteur d'inférence.",
      "· Chaque interaction IA est tracée : avant, après, jetons.",
      "· La propriété est dans le WHERE, et renvoie 404.",
      "",
      "Merci de votre attention.",
      ...(OLLAMA_REEL
        ? []
        : ["", "Enregistré sans Ollama : le moteur d'inférence est substitué.", "Tout le reste — interface, API, base, contrôles — est réel."]),
    ],
    "HelpMeDraft",
  );
  await pause(7000);
});

// ─────────────────────────── exécution ───────────────────────────

mkdirSync(SORTIE, { recursive: true });

const navigateur = await chromium.launch({ args: ["--no-sandbox", "--force-device-scale-factor=1"] });
const contexte = await navigateur.newContext({
  viewport: { width: 1440, height: 900 },
  recordVideo: { dir: SORTIE, size: { width: 1440, height: 900 } },
  locale: "fr-FR",
  timezoneId: "Europe/Paris",
  reducedMotion: "no-preference",
});
const page = await contexte.newPage();

// Masque le curseur de saisie clignotant, qui scintille à l'encodage.
await contexte.addInitScript(() => {
  const style = document.createElement("style");
  style.textContent = "*{caret-color:#C4341C!important}";
  document.documentElement.appendChild(style);
});

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
    await page.screenshot({ path: join(SORTIE, `echec-${rang}-${titre.replace(/\W+/g, "-")}.png`) }).catch(() => {});
  }
}

await contexte.close();
await navigateur.close();

const brut = readdirSync(SORTIE).find((f) => f.endsWith(".webm") && !f.startsWith("demo-"));
if (brut) {
  renameSync(join(SORTIE, brut), join(SORTIE, "demo-helpmedraft.webm"));
  console.log(`\nVidéo : ${join(SORTIE, "demo-helpmedraft.webm")}`);
  console.log("Conversion MP4 :");
  console.log(`  ffmpeg -i ${join(SORTIE, "demo-helpmedraft.webm")} -c:v libx264 -preset slow -crf 23 -pix_fmt yuv420p ${join(SORTIE, "demo-helpmedraft.mp4")}`);
}
