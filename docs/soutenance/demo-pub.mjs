/**
 * Vidéo de démonstration façon publicité — environ 75 s, avec nappe musicale.
 *
 * Trois temps, enchaînés par ce seul script :
 *   1. captation. Un Chromium réel parcourt l'application ; le script relève
 *      l'instant de chaque plan dans la vidéo brute.
 *   2. montage. ffmpeg coupe ces passages, règle la vitesse de chacun sur la
 *      durée voulue, et les colle bout à bout.
 *   3. musique. musique.py synthétise une nappe à la durée exacte du montage,
 *      puis ffmpeg la mélange à l'image.
 *
 * Tout ce qu'on voit est l'application. Les quelques phrases sont posées dans
 * la page, à la charte de l'app.
 *
 * PRÉREQUIS : backend (5000), frontend (5173), Ollama (11434), et la base
 * chargée par `python database/jeu_essai.py --vider`.
 *
 *   node docs/soutenance/demo-pub.mjs [sortie.mp4]
 */

import { mkdirSync, rmSync, existsSync, writeFileSync, readdirSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { join, resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

const exiger = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = await import("playwright")); }
catch { ({ chromium } = exiger("playwright")); }

const ICI = dirname(fileURLToPath(import.meta.url));
const BASE = process.env.DEMO_URL ?? "http://localhost:5173";
const API = process.env.DEMO_API ?? "http://localhost:5000";
const MDP = process.env.DEMO_MDP ?? "JeuDEssai1";
const SORTIE = resolve(process.argv[2] ?? join(ICI, "demo-pub-helpmedraft.mp4"));
const TRAVAIL = join(dirname(SORTIE), ".demo-pub-travail");

const pause = (ms) => new Promise((r) => setTimeout(r, ms));

const OLLAMA_REEL = await fetch(`${process.env.OLLAMA_URL ?? "http://127.0.0.1:11434"}/api/version`)
  .then((r) => r.ok).catch(() => false);

// ── la phrase posée en bas de l'écran ───────────────────────────────
const BANDEAU = `
(() => {
  if (document.getElementById('__pub')) return;
  const b = document.createElement('div');
  b.id = '__pub';
  b.style.cssText = [
    'position:fixed','bottom:46px','left:0','z-index:2147483647',
    'background:#111111','color:#F4F1EA','padding:22px 40px 22px 56px',
    'font:700 36px/1.2 Georgia,"Charter",serif','letter-spacing:.2px',
    'border-top:7px solid #E0533C','border-right:7px solid #E0533C',
    'pointer-events:none','opacity:0','max-width:1050px',
    'transition:opacity .3s ease, transform .3s ease','transform:translateX(-14px)',
  ].join(';');
  document.body.appendChild(b);
})();`;

async function phrase(page, texte) {
  await page.evaluate(BANDEAU).catch(() => {});
  await page.evaluate((t) => {
    const b = document.getElementById("__pub");
    if (!b) return;
    if (t) b.textContent = t;
    b.style.opacity = t ? "1" : "0";
    b.style.transform = t ? "translateX(0)" : "translateX(-14px)";
  }, texte).catch(() => {});
}

// ── captation ───────────────────────────────────────────────────────
if (existsSync(TRAVAIL)) rmSync(TRAVAIL, { recursive: true, force: true });
mkdirSync(TRAVAIL, { recursive: true });

const navigateur = await chromium.launch({ args: ["--no-sandbox", "--force-device-scale-factor=1"] });
const contexte = await navigateur.newContext({
  viewport: { width: 1600, height: 900 },
  recordVideo: { dir: TRAVAIL, size: { width: 1600, height: 900 } },
  locale: "fr-FR", timezoneId: "Europe/Paris",
});
await contexte.addInitScript(() => {
  const s = document.createElement("style");
  s.textContent = "*{caret-color:#C4341C!important}";
  document.documentElement.appendChild(s);
});
const page = await contexte.newPage();

const t0 = Date.now();
const maintenant = () => (Date.now() - t0) / 1000;
const reperes = [];
let recalage = null;
const depuisIci = () => { recalage = maintenant(); };

async function plan(nom, fn) {
  const ouverture = maintenant();
  recalage = null;
  try { await fn(); } catch (e) { console.log(`   (${nom} : ${e.message.split("\n")[0]})`); }
  reperes.push({ nom, debut: recalage ?? ouverture, fin: maintenant() });
  console.log(`   ${nom.padEnd(12)} ${(recalage ?? ouverture).toFixed(1)} → ${maintenant().toFixed(1)} s`);
}

console.log("  captation…");

await plan("accueil", async () => {
  await page.goto(BASE, { waitUntil: "networkidle" });
  await pause(1000);
  await phrase(page, "Écrire vite. Écrire juste.");
  await pause(2200);
  for (let i = 0; i < 9; i++) { await page.mouse.wheel(0, 210); await pause(260); }
  await pause(1000);
});

await plan("connexion", async () => {
  await phrase(page, "");
  await page.goto(`${BASE}/login`, { waitUntil: "networkidle" });
  await pause(600);
  await page.fill("#email", "camille@helpmedraft.test");
  await pause(300);
  await page.fill("#mdp", MDP);
  await pause(500);
  await page.getByRole("button", { name: /se connecter|connexion/i }).first().click();
  await page.waitForURL(/dashboard/, { timeout: 15000 }).catch(() => {});
  await pause(1600);
});

await plan("bureau", async () => {
  await phrase(page, "Tout votre travail, au même endroit.");
  await pause(2200);
  await page.mouse.wheel(0, 330);
  await pause(1900);
  await page.mouse.wheel(0, 330);
  await pause(1700);
});

await plan("documents", async () => {
  await phrase(page, "Vos documents, classés en dossiers.");
  await page.goto(`${BASE}/documents`, { waitUntil: "networkidle" });
  await pause(2600);
  await page.mouse.wheel(0, 260);
  await pause(1500);
});

await plan("brouillon", async () => {
  await phrase(page, "");
  await page.goto(`${BASE}/documents/nouveau`, { waitUntil: "networkidle" });
  await pause(800);
  await page.locator('input[type="text"]').first().click();
  await page.keyboard.insertText("Relance commande 4812");
  await pause(600);
  const zone = page.getByRole("textbox", { name: /Éditeur de document/i }).first();
  await zone.click();
  await phrase(page, "Un brouillon, écrit vite.");
  depuisIci();
  for (const m of "bjr, jai commandé le 12 octobre et jai toujours rien recu. pouvez vous me dire ou elle en est svp".split(/(?<=\s)/)) {
    await page.keyboard.insertText(m);
    await pause(150);
  }
  await pause(6000);
});

await plan("assistant", async () => {
  await phrase(page, "Trois commandes : reformuler, corriger, compléter.");
  await page.locator('button[title="Assistant IA"]').first().click();
  await pause(2000);
  await page.locator("select").filter({ has: page.locator('option[value="reformuler"]') }).first()
    .selectOption("reformuler").catch(() => {});
  await pause(900);
  await page.locator("select").filter({ has: page.locator('option[value="selection"]') }).first()
    .selectOption("document").catch(() => {});
  await pause(2800);
});

await plan("generation", async () => {
  await phrase(page, OLLAMA_REEL
    ? "Le modèle tourne sur votre machine."
    : "Le modèle tourne sur votre machine.");
  depuisIci();
  await page.getByRole("button", { name: /^Générer$/ }).first().click();
  await page.getByRole("button", { name: /remplacer/i }).first().waitFor({ timeout: 120000 });
  await pause(4800);
});

await plan("resultat", async () => {
  await phrase(page, "Une lettre présentable, en quelques secondes.");
  await page.getByRole("button", { name: /remplacer/i }).first().click();
  await pause(7400);
});

await plan("trace", async () => {
  await phrase(page, "Et on sait toujours ce que l'IA a écrit.");
  const b = page.getByRole("button", { name: /Passages issus/i }).first();
  if (await b.isVisible().catch(() => false)) { await b.click(); await pause(2400); await page.mouse.wheel(0, 220); await pause(4800); }
  else await pause(7400);
});

await plan("admin", async () => {
  await phrase(page, "");
  // Déconnexion par le vrai bouton : le front passe par le proxy /api de Vite,
  // qui réécrit le chemin du cookie de refresh. Un appel direct au port 5000
  // ne porterait pas ce cookie, et la session resterait ouverte.
  await page.getByRole("button", { name: /Déconnexion/i }).first().click();
  await page.waitForURL(/\/$|login/, { timeout: 15000 }).catch(() => {});
  await pause(900);
  await page.goto(`${BASE}/login`, { waitUntil: "networkidle" });
  await page.waitForSelector("#email", { timeout: 15000 });
  await page.fill("#email", "admin@helpmedraft.test");
  await page.fill("#mdp", MDP);
  await page.getByRole("button", { name: /se connecter|connexion/i }).first().click();
  await page.waitForURL(/dashboard|admin/, { timeout: 15000 }).catch(() => {});
  await page.goto(`${BASE}/admin`, { waitUntil: "networkidle" });
  depuisIci();
  await phrase(page, "Comptes, quotas, statistiques.");
  await pause(3400);
  await page.mouse.wheel(0, 380);
  await pause(3600);
});

await plan("final", async () => {
  await phrase(page, "");
  await page.goto(`${BASE}/dashboard`, { waitUntil: "networkidle" });
  await pause(700);
  depuisIci();
  await page.evaluate((reel) => {
    const v = document.createElement("div");
    v.style.cssText = [
      "position:fixed","inset:0","z-index:2147483646",
      "background:rgba(17,17,17,.975)","color:#F4F1EA",
      "display:flex","flex-direction:column","justify-content:center",
      "padding:0 9vw","font-family:Georgia,'Charter',serif",
    ].join(";");
    const l = document.createElement("div");
    l.style.cssText = "display:flex;align-items:center;gap:26px;margin-bottom:36px";
    const c = document.createElement("div");
    c.textContent = "H";
    c.style.cssText = "width:92px;height:92px;background:#E0533C;color:#111;font:700 54px/92px Georgia,serif;text-align:center";
    const n = document.createElement("div");
    n.textContent = "HelpMeDraft";
    n.style.cssText = "font-size:88px;font-weight:700";
    l.append(c, n);
    const a = document.createElement("div");
    a.textContent = "L'IA qui ne sort jamais de chez vous.";
    a.style.cssText = "font-size:52px;font-weight:700";
    const p = document.createElement("div");
    p.textContent = "INFÉRENCE 100 % LOCALE · RGPD PAR CONSTRUCTION";
    p.style.cssText = 'margin-top:32px;color:#E0533C;font:700 21px/1 "JetBrains Mono",monospace;letter-spacing:5px';
    v.append(l, a, p);
    if (!reel) {
      const m = document.createElement("div");
      m.textContent = "Enregistré sans Ollama : le moteur d'inférence est substitué. Tout le reste est réel.";
      m.style.cssText = "position:absolute;left:9vw;bottom:54px;font-size:18px;opacity:.55;max-width:70vw";
      v.appendChild(m);
    }
    document.body.appendChild(v);
  }, OLLAMA_REEL);
  await pause(8600);
});

await contexte.close();
await navigateur.close();

// ── montage ─────────────────────────────────────────────────────────
const brut = join(TRAVAIL, readdirSync(TRAVAIL).find((f) => f.endsWith(".webm")));
writeFileSync(join(TRAVAIL, "reperes.json"), JSON.stringify(reperes, null, 2));

// Durée visée de chaque plan. La somme donne la durée du film, et donc celle
// de la musique : on la synthétise ensuite à la seconde près.
const MONTAGE = [
  ["accueil",    8.0],
  ["connexion",  3.5],
  ["bureau",     6.5],
  ["documents",  5.0],
  ["brouillon",  8.5],
  ["assistant",  6.0],
  ["generation", 7.5],
  ["resultat",   7.0],
  ["trace",      7.0],
  ["admin",      6.5],
  ["final",      8.0],
];

console.log("\n  montage…");
const morceaux = [];
let duree = 0;
for (const [nom, cible] of MONTAGE) {
  const r = reperes.find((x) => x.nom === nom);
  if (!r) continue;
  const source = Math.max(0.4, r.fin - r.debut);
  // Jamais en dessous de 1 : ralentir se voit, accélérer non.
  const vitesse = Math.max(1.0, source / cible);
  const reelle = source / vitesse;
  const fichier = join(TRAVAIL, `plan-${nom}.mp4`);
  execFileSync("ffmpeg", [
    "-y", "-loglevel", "error",
    "-ss", r.debut.toFixed(3), "-t", source.toFixed(3), "-i", brut,
    "-vf", `setpts=PTS/${vitesse.toFixed(5)},fps=30,scale=1600:900:flags=lanczos`,
    "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
    fichier,
  ]);
  morceaux.push(fichier);
  duree += reelle;
  const alerte = reelle < cible - 0.3 ? "  ← prise trop courte" : "";
  console.log(`   ${nom.padEnd(11)} ${source.toFixed(1)} s → ${reelle.toFixed(1)} s  (×${vitesse.toFixed(2)})${alerte}`);
}

const liste = join(TRAVAIL, "liste.txt");
writeFileSync(liste, morceaux.map((f) => `file '${f}'`).join("\n"));
const muet = join(TRAVAIL, "muet.mp4");
execFileSync("ffmpeg", ["-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", liste,
  "-c:v", "libx264", "-preset", "slow", "-crf", "21", "-pix_fmt", "yuv420p", muet]);

// ── musique ─────────────────────────────────────────────────────────
console.log(`\n  musique (${duree.toFixed(0)} s)…`);
const wav = join(TRAVAIL, "musique.wav");
execFileSync("python3", ["-I", join(ICI, "musique.py"), wav, duree.toFixed(2)], { stdio: "inherit" });

execFileSync("ffmpeg", [
  "-y", "-loglevel", "error",
  "-i", muet, "-i", wav,
  "-c:v", "copy",
  "-c:a", "aac", "-b:a", "192k", "-ac", "2",
  "-shortest", "-movflags", "+faststart",
  SORTIE,
], { stdio: "inherit" });

console.log(`\nVidéo : ${SORTIE}`);
