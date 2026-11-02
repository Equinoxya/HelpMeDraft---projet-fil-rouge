/**
 * Pub d'ouverture — 20 s, montée à partir du SITE lui-même.
 *
 * Deux temps :
 *   1. captation. Un Chromium réel parcourt l'application. Le script relève
 *      l'instant de chaque temps fort dans la vidéo brute.
 *   2. montage. ffmpeg coupe ces passages, les accélère chacun au rythme
 *      voulu, et les colle bout à bout pour tomber sur 20 s.
 *
 * Aucun carton typographique : tout ce qu'on voit est l'application. Les
 * quelques mots affichés sont posés dans la page, en haut à gauche, à la
 * charte de l'app.
 *
 * PRÉREQUIS : backend (5000), frontend (5173), Ollama (11434), et la base
 * chargée par `python database/jeu_essai.py --vider`.
 *
 *   node docs/soutenance/pub-20s.mjs [sortie.mp4]
 */

import { mkdirSync, rmSync, existsSync, writeFileSync } from "node:fs";
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
const SORTIE = resolve(process.argv[2] ?? join(ICI, "pub-helpmedraft.mp4"));
const TRAVAIL = join(dirname(SORTIE), ".pub-travail");

const pause = (ms) => new Promise((r) => setTimeout(r, ms));

// ── le mot posé en haut à gauche ────────────────────────────────────
const BANDEAU = `
(() => {
  if (document.getElementById('__pub')) return;
  const b = document.createElement('div');
  b.id = '__pub';
  b.style.cssText = [
    'position:fixed','bottom:0','left:0','z-index:2147483647',
    'background:#111111','color:#F4F1EA','padding:18px 30px',
    'font:700 27px/1.25 Georgia,"Charter",serif',
    'border-right:6px solid #E0533C','border-top:6px solid #E0533C',
    'pointer-events:none','opacity:0','transition:opacity .18s','max-width:720px',
  ].join(';');
  document.body.appendChild(b);
})();`;

async function mot(page, texte) {
  await page.evaluate(BANDEAU).catch(() => {});
  await page.evaluate((t) => {
    const b = document.getElementById("__pub");
    if (!b) return;
    b.textContent = t;
    b.style.opacity = t ? "1" : "0";
  }, texte).catch(() => {});
}

// ── captation ───────────────────────────────────────────────────────

if (existsSync(TRAVAIL)) rmSync(TRAVAIL, { recursive: true, force: true });
mkdirSync(TRAVAIL, { recursive: true });

const navigateur = await chromium.launch({ args: ["--no-sandbox", "--force-device-scale-factor=1"] });
const contexte = await navigateur.newContext({
  viewport: { width: 1600, height: 900 },
  recordVideo: { dir: TRAVAIL, size: { width: 1600, height: 900 } },
  locale: "fr-FR",
  timezoneId: "Europe/Paris",
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
/** Depuis un plan : « le montage commence ici », pas au premier octet. */
const depuisIci = () => { recalage = maintenant(); };

/** Ouvre un plan, exécute, et note ses bornes dans la vidéo brute. */
async function plan(nom, fn) {
  const ouverture = maintenant();
  recalage = null;
  try { await fn(); } catch (e) { console.log(`   (${nom} : ${e.message.split("\n")[0]})`); }
  const debut = recalage ?? ouverture;
  reperes.push({ nom, debut, fin: maintenant() });
  console.log(`   ${nom.padEnd(14)} ${debut.toFixed(1)} → ${maintenant().toFixed(1)} s`);
}

console.log("  captation…");

await plan("accueil", async () => {
  await page.goto(BASE, { waitUntil: "networkidle" });
  await pause(900);
  await mot(page, "Vos écrits professionnels.");
  await pause(1400);
  for (let i = 0; i < 7; i++) { await page.mouse.wheel(0, 230); await pause(230); }
  await pause(700);
});

await plan("connexion", async () => {
  await mot(page, "");
  await page.goto(`${BASE}/login`, { waitUntil: "networkidle" });
  await pause(500);
  await page.fill("#email", "camille@helpmedraft.test");
  await pause(250);
  await page.fill("#mdp", MDP);
  await pause(450);
  await page.getByRole("button", { name: /se connecter|connexion/i }).first().click();
  await page.waitForURL(/dashboard/, { timeout: 15000 }).catch(() => {});
  await pause(1600);
});

await plan("bureau", async () => {
  await mot(page, "Tout votre travail, au même endroit.");
  await pause(1700);
  await page.mouse.wheel(0, 380);
  await pause(1600);
});

await plan("brouillon", async () => {
  await mot(page, "");
  await page.goto(`${BASE}/documents/nouveau`, { waitUntil: "networkidle" });
  await pause(700);
  await page.locator('input[type="text"]').first().click();
  await page.keyboard.insertText("Relance commande 4812");
  await pause(500);
  const zone = page.getByRole("textbox", { name: /Éditeur de document/i }).first();
  await zone.click();
  await mot(page, "Un brouillon, écrit vite.");
  depuisIci();
  for (const m of "bjr, jai commandé le 12 octobre et jai toujours rien recu. pouvez vous me dire ou elle en est svp".split(/(?<=\s)/)) {
    await page.keyboard.insertText(m);
    await pause(85);
  }
  await pause(1200);
});

await plan("appel", async () => {
  await mot(page, "Une touche.");
  await page.locator('button[title="Assistant IA"]').first().click();
  await pause(1300);
  await page.locator("select").filter({ has: page.locator('option[value="reformuler"]') }).first()
    .selectOption("reformuler").catch(() => {});
  await page.locator("select").filter({ has: page.locator('option[value="selection"]') }).first()
    .selectOption("document").catch(() => {});
  await pause(800);
  depuisIci();
  await page.getByRole("button", { name: /^Générer$/ }).first().click();
  await mot(page, "Le modèle tourne sur votre machine.");
  await page.getByRole("button", { name: /remplacer/i }).first().waitFor({ timeout: 120000 });
  await pause(1400);
});

await plan("resultat", async () => {
  await mot(page, "Une lettre présentable.");
  await page.getByRole("button", { name: /remplacer/i }).first().click();
  await pause(2600);
});

await plan("trace", async () => {
  await mot(page, "Et on sait toujours ce que l'IA a écrit.");
  const b = page.getByRole("button", { name: /Passages issus/i }).first();
  if (await b.isVisible().catch(() => false)) { await b.click(); await pause(2400); }
  else await pause(1500);
});

await plan("final", async () => {
  await mot(page, "");
  await page.goto(`${BASE}/dashboard`, { waitUntil: "networkidle" });
  await pause(600);
  // Le dernier plan reste le site : on le voile, on pose la marque dessus.
  await page.evaluate(() => {
    const v = document.createElement("div");
    v.id = "__fin";
    v.style.cssText = [
      "position:fixed","inset:0","z-index:2147483646",
      "background:rgba(17,17,17,.93)","color:#F4F1EA",
      "display:flex","flex-direction:column","justify-content:center",
      "padding:0 9vw","font-family:Georgia,'Charter',serif",
    ].join(";");
    const l = document.createElement("div");
    l.style.cssText = "display:flex;align-items:center;gap:24px;margin-bottom:34px";
    const c = document.createElement("div");
    c.textContent = "H";
    c.style.cssText = "width:86px;height:86px;background:#E0533C;color:#111;font:700 50px/86px Georgia,serif;text-align:center";
    const n = document.createElement("div");
    n.textContent = "HelpMeDraft";
    n.style.cssText = "font-size:84px;font-weight:700";
    l.append(c, n);
    const a = document.createElement("div");
    a.textContent = "L'IA qui ne sort jamais de chez vous.";
    a.style.cssText = "font-size:50px;font-weight:700";
    const p = document.createElement("div");
    p.textContent = "INFÉRENCE 100 % LOCALE · RGPD PAR CONSTRUCTION";
    p.style.cssText = 'margin-top:30px;color:#E0533C;font:700 20px/1 "JetBrains Mono",monospace;letter-spacing:5px';
    v.append(l, a, p);
    document.body.appendChild(v);
  });
  await pause(3200);
});

await contexte.close();
await navigateur.close();

// ── montage ─────────────────────────────────────────────────────────

const { readdirSync } = await import("node:fs");
const brut = join(TRAVAIL, readdirSync(TRAVAIL).find((f) => f.endsWith(".webm")));
writeFileSync(join(TRAVAIL, "reperes.json"), JSON.stringify(reperes, null, 2));

// Durée visée pour chaque plan au montage. La somme fait 20 s ; chaque plan
// est accéléré de ce qu'il faut pour y tenir.
const MONTAGE = [
  ["accueil",   3.2],
  ["connexion", 1.2],
  ["bureau",    2.0],
  ["brouillon", 2.8],
  ["appel",     2.3],
  ["resultat",  2.3],
  ["trace",     2.4],
  ["final",     3.8],
];

console.log("\n  montage…");
const morceaux = [];
for (const [nom, cible] of MONTAGE) {
  const r = reperes.find((x) => x.nom === nom);
  if (!r) continue;
  const source = Math.max(0.4, r.fin - r.debut);
  const vitesse = source / cible; // > 1 : on accélère
  const fichier = join(TRAVAIL, `plan-${nom}.mp4`);
  execFileSync("ffmpeg", [
    "-y", "-loglevel", "error",
    "-ss", r.debut.toFixed(3), "-t", source.toFixed(3), "-i", brut,
    "-vf", `setpts=PTS/${vitesse.toFixed(5)},fps=30,scale=1600:900:flags=lanczos`,
    "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
    fichier,
  ]);
  morceaux.push(fichier);
  console.log(`   ${nom.padEnd(10)} ${source.toFixed(1)} s → ${cible} s  (×${vitesse.toFixed(2)})`);
}

const liste = join(TRAVAIL, "liste.txt");
writeFileSync(liste, morceaux.map((f) => `file '${f}'`).join("\n"));
execFileSync("ffmpeg", [
  "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", liste,
  "-c:v", "libx264", "-preset", "slow", "-crf", "21", "-pix_fmt", "yuv420p",
  "-movflags", "+faststart", SORTIE,
], { stdio: "inherit" });

console.log(`\nPub : ${SORTIE}`);
