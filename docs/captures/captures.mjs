/**
 * Production des captures d'interfaces C-01 à C-11 (dossier § 7.1 et annexe § 12.2).
 *
 * POURQUOI UN SCRIPT PLUTÔT QUE DES CAPTURES À LA MAIN
 *
 * Une série refaite à la main ne se compare pas d'une fois sur l'autre : la
 * largeur dérive, le compte connecté change, un survol reste accroché à un
 * bouton. Or la série DOIT être refaite à chaque évolution de l'interface —
 * elle l'a été après la refonte de l'éditeur, qui a rendu caduques C-05 et C-07.
 *
 * PRÉALABLES
 *
 *   1. une base jetable chargée avec le jeu d'essai du dépôt :
 *        cd backend
 *        HELPMEDRAFT_DB_URL="sqlite:///captures.db" python database/jeu_essai.py
 *   2. le backend sur le port 5000 et Vite sur le 5173, sur cette même base ;
 *   3. pour C-11 seulement, un jeton de réinitialisation valide, créé en base
 *      et passé par la variable d'environnement JETON_REINIT. Sans lui, la
 *      capture montre l'écran de jeton invalide.
 *
 * LANCEMENT
 *
 *   JETON_REINIT="<jeton>" node docs/captures/captures.mjs
 *
 * Les dimensions sont celles de la première série : voir INDEX.md, qui explique
 * pourquoi elles ne doivent pas changer.
 */

import { chromium } from 'playwright';

const BASE = 'http://localhost:5173';
const SORTIE = new URL('.', import.meta.url).pathname;
const JETON = process.env.JETON_REINIT || '';

// Dimensions reprises des captures existantes, pour que les largeurs calées
// dans docs/dossier/fill_trame.py gardent la même hauteur rendue dans le Word.
const BUREAU = { width: 1654, height: 1272 };
const MOBILE = { width: 496, height: 855 };

const faits = [];
async function prendre(page, fichier, options = {}) {
  // La souris est écartée : après un clic, le bouton survolé reste en
  // surbrillance et la capture montre un état transitoire.
  await page.mouse.move(4, 4);
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(400);
  await page.screenshot({ path: `${SORTIE}/${fichier}`, ...options });
  faits.push(fichier);
  console.log(`  ✓ ${fichier}`);
}

async function connecter(page, email) {
  await page.goto(`${BASE}/login`);
  await page.locator('input[type=email]').fill(email);
  await page.locator('input[type=password]').first().fill('JeuDEssai1');
  await page.locator('form button[type=submit]').first().click();
  await page.waitForURL(/\/dashboard/, { timeout: 20000 });
}

const browser = await chromium.launch();

// ── Écrans publics (C-01 à C-04, C-11) ──────────────────────────────────────
{
  const ctx = await browser.newContext({ viewport: BUREAU });
  const page = await ctx.newPage();

  await page.goto(`${BASE}/`);
  await prendre(page, 'C-01-accueil.png', { fullPage: true });

  await page.goto(`${BASE}/login`);
  await prendre(page, 'C-02-connexion.png');

  await page.goto(`${BASE}/register`);
  await prendre(page, 'C-03-inscription.png', { fullPage: true });

  await page.goto(`${BASE}/forgot-password`);
  await prendre(page, 'C-04-mot-de-passe-oublie.png');

  // C-11 : jeton réellement valide, créé en base pour cette capture.
  await page.goto(`${BASE}/reset-password?token=${JETON}`);
  await prendre(page, 'C-11-reinitialisation.png');

  await ctx.close();
}

// ── Accueil mobile (C-01b) ──────────────────────────────────────────────────
{
  const ctx = await browser.newContext({ viewport: MOBILE, isMobile: true, hasTouch: true });
  const page = await ctx.newPage();
  await page.goto(`${BASE}/`);
  await prendre(page, 'C-01b-accueil-mobile.png');
  await ctx.close();
}

// ── Espace de Camille : 5 documents, 15 appels IA sur 20 (C-05 à C-09) ──────
{
  const ctx = await browser.newContext({ viewport: BUREAU });
  const page = await ctx.newPage();
  await connecter(page, 'camille@helpmedraft.test');

  await prendre(page, 'C-05-tableau-de-bord.png', { fullPage: true });

  await page.goto(`${BASE}/documents`);
  await prendre(page, 'C-06-liste-documents.png');

  await page.goto(`${BASE}/documents/nouveau`);
  await page.waitForSelector('.cm-content');
  await prendre(page, 'C-07-nouveau-document.png');

  // C-08 : un document EXISTANT chargé, et non la création.
  //
  // Le lien doit pointer sur un identifiant, pas sur /documents/nouveau ni
  // /documents/importer : un premier essai avait attrapé « Nouveau document »
  // et produit une capture d'éditeur vide, en-tête « nouveau brouillon ».
  await page.goto(`${BASE}/documents`);
  await page.waitForLoadState('networkidle');
  // Le document est choisi par son TITRE, et non « le premier de la liste » :
  // le jeu d'essai contient à dessein un « Document vierge », cas limite sans
  // contenu, qui donnerait une capture d'éditeur vide — exactement ce qu'une
  // annexe d'interface ne doit pas montrer.
  const lien = page.getByRole('link', { name: /Note de service — terminée/ }).first();
  const cible = await lien.getAttribute('href');
  console.log(`    document ouvert : ${cible}`);
  await lien.click();
  await page.waitForURL(/\/documents\/[0-9a-f-]{8,}/, { timeout: 20000 });
  await page.waitForSelector('.cm-content', { timeout: 20000 });
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(1000);
  await prendre(page, 'C-08-editeur-document.png');

  // C-09 : le panneau de l'assistant IA ouvert sur ce même document chargé.
  await page.locator('[role=toolbar] button', { hasText: 'IA' }).first().click();
  await page.waitForTimeout(600);
  const panneau = page.getByText('[ Assistant IA — Ollama ]');
  if (await panneau.count()) {
    await panneau.scrollIntoViewIfNeeded();
    await page.waitForTimeout(400);
    await prendre(page, 'C-09-assistant-ia.png');
  } else {
    console.log('  ! panneau IA introuvable');
  }

  await ctx.close();
}

// ── Back-office (C-10) ──────────────────────────────────────────────────────
{
  const ctx = await browser.newContext({ viewport: BUREAU });
  const page = await ctx.newPage();
  await connecter(page, 'admin@helpmedraft.test');
  await page.goto(`${BASE}/admin`);
  await prendre(page, 'C-10-back-office.png');
  await ctx.close();
}

await browser.close();
console.log(`\n${faits.length} captures produites.`);
