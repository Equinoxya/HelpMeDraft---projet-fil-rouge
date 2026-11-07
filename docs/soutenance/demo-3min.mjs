/**
 * Captation vidéo — démonstration longue, environ trois minutes
 *
 * Même machinerie que la version courte (demo-commun.mjs), parcours plus
 * complet : les pages publiques, l'inscription, les dossiers, l'export PDF
 * et la vue mobile s'ajoutent au cœur de la démonstration — l'assistant IA,
 * la traçabilité, le quota, le cloisonnement, le back-office.
 *
 * Pas de musique, pas de montage : les sous-titres sont gravés dans la page
 * pendant la captation, et le fichier produit est directement diffusable.
 *
 * PRÉREQUIS
 *   1. backend  : cd backend && python run.py                   (port 5000)
 *   2. frontend : cd frontend && npm run dev                    (port 5173)
 *   3. base     : cd backend && python database/jeu_essai.py --vider
 *   4. Ollama   : ollama serve + ollama pull qwen2.5:3b          (port 11434)
 *
 * Sans Ollama joignable, le parcours applicatif reste réel — contrôles,
 * quota, journalisation — mais la vidéo DIT que le modèle est substitué.
 *
 * LANCEMENT
 *   node docs/soutenance/demo-3min.mjs [dossier-de-sortie]
 */

import { resolve } from "node:path";
import {
  BASE, COMPTES, MDP, OLLAMA_REEL,
  appelApi, carte, connexion, deconnexion, executer, frapper, frapperEditeur,
  pause, retirerCarte, scenario, soustitre,
} from "./demo-commun.mjs";

const SORTIE = resolve(process.argv[2] ?? "docs/soutenance/demo3");
const { etapes, etape } = scenario();

// Identifiant d'un document appartenant à Karim, relevé pendant l'étape du
// quota. L'étape de cloisonnement le redemandera sous le compte de Camille :
// c'est ce qui en fait une vraie preuve de cloisonnement, et non un simple
// identifiant inexistant qui renverrait 404 pour une autre raison.
let docDAutrui = process.env.DEMO_DOC_AUTRUI ?? "00000000-0000-0000-0000-000000000000";

// ─────────────────────────── 1. le produit ───────────────────────────

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
  await pause(5000);
  await retirerCarte(page);
  await soustitre(page, "Page d'accueil", "Le produit et sa promesse : une IA qui ne sort pas de chez vous.");
  await pause(2600);
  await page.mouse.wheel(0, 620);
  await pause(2400);
  await page.mouse.wheel(0, 700);
  await pause(2200);
});

etape("Pages publiques", async (page) => {
  await page.goto(`${BASE}/fonctionnalites`, { waitUntil: "networkidle" });
  await soustitre(page, "Pages publiques", "Vitrine, tarifs, et les trois pages légales — mentions, CGU, confidentialité.");
  await pause(2800);
  await page.mouse.wheel(0, 700);
  await pause(2200);
  await page.goto(`${BASE}/confidentialite`, { waitUntil: "networkidle" });
  await soustitre(page, "Confidentialité", "La politique dit où vont les données. Ici, la réponse est : elles ne sortent pas.");
  await pause(3200);
});

etape("Inscription", async (page) => {
  await page.goto(`${BASE}/register`, { waitUntil: "networkidle" });
  await soustitre(page, "Inscription", "Le mot de passe est haché en bcrypt ; la règle de robustesse est vérifiée des deux côtés.");
  await pause(2600);
  const champs = page.locator('input[type="text"], input[type="email"]');
  if (await champs.first().isVisible().catch(() => false)) {
    await frapper(champs.first(), "Camille", 45);
    await pause(400);
  }
  await page.mouse.wheel(0, 320);
  await pause(3400);
  await soustitre(page, "Inscription", "Les comptes du jeu d'essai sont déjà créés : la suite se fait avec l'un d'eux.");
  await pause(2400);
});

// ─────────────────────────── 2. l'espace de travail ───────────────────────────

etape("Connexion", async (page) => {
  await page.goto(`${BASE}/login`, { waitUntil: "networkidle" });
  await soustitre(page, "Authentification", "Access token de 15 minutes, refresh token de 7 jours révocable côté serveur.");
  await pause(1600);
  await frapper(page.locator("#email"), COMPTES.camille, 40);
  await pause(300);
  await frapper(page.locator("#mdp"), MDP, 55);
  await pause(800);
  await page.getByRole("button", { name: /se connecter|connexion/i }).first().click();
  await page.waitForURL(/dashboard/, { timeout: 15000 }).catch(() => {});
  await pause(1400);
});

etape("Tableau de bord", async (page) => {
  await soustitre(page, "Tableau de bord", "Les compteurs viennent de l'API, pas d'un calcul côté navigateur.");
  await pause(3000);
  await page.mouse.wheel(0, 420);
  await soustitre(page, "Tableau de bord", "Trois portes d'entrée vers la rédaction : supprimer la page blanche.");
  await pause(3400);
  await page.mouse.wheel(0, 380);
  await pause(2800);
  await page.mouse.wheel(0, -800);
  await pause(700);
});

etape("Dossiers et recherche", async (page) => {
  await page.goto(`${BASE}/documents`, { waitUntil: "networkidle" });
  await soustitre(page, "Mes documents", "Pagination serveur : la liste n'est jamais chargée entièrement.");
  await pause(3400);

  const nouveau = page.getByRole("button", { name: /Nouveau dossier/i }).first();
  if (await nouveau.isVisible().catch(() => false)) {
    await soustitre(page, "Dossiers", "Un document appartient à un dossier, ou à aucun — jamais à deux.");
    await nouveau.click();
    await pause(700);
    await frapper(page.locator('input[placeholder="Nom du dossier"]').first(), "Réclamations", 55);
    await pause(600);
    await page.getByRole("button", { name: /^Créer$/ }).first().click();
    await pause(2400);
  }

  const recherche = page.getByLabel(/Rechercher un document/i).first();
  if (await recherche.isVisible().catch(() => false)) {
    await soustitre(page, "Recherche", "Le filtre porte sur la page affichée ; le tri et la pagination restent au serveur.");
    await frapper(recherche, "commande", 70);
    await pause(2600);
    await recherche.fill("");
    await pause(900);
  }
});

// ─────────────────────────── 3. rédiger, et faire appel au modèle ──────────────

etape("Éditeur et enregistrement automatique", async (page) => {
  await page.goto(`${BASE}/documents/nouveau`, { waitUntil: "networkidle" });
  await pause(900);
  await soustitre(page, "Éditeur", "Rien n'est enregistré tant que le titre est vide.");
  await pause(2200);

  const titre = page.locator('input[type="text"]').first();
  await titre.click();
  await frapper(titre, "Relance commande 4812", 55);
  await pause(600);

  await soustitre(page, "Éditeur", "L'enregistrement part 2,5 s après la dernière frappe — et un bouton permet de forcer.");
  const zone = page.getByRole("textbox", { name: /Éditeur de document/i }).first();
  await frapperEditeur(
    page,
    zone,
    "bjr, jai commandé le 12 octobre la commande 4812 et jai toujours rien recu. pouvez vous me dire ou elle en est svp",
  );
  await pause(3800);
});

etape("Génération IA", async (page) => {
  await soustitre(page, "Assistant IA", "Trois actions, et trois seulement : reformuler, corriger, compléter.");
  await page.locator('button[title="Assistant IA"]').first().click();
  await pause(2000);

  const selAction = page.locator("select").filter({ has: page.locator('option[value="reformuler"]') }).first();
  const selPortee = page.locator("select").filter({ has: page.locator('option[value="selection"]') }).first();
  await selAction.selectOption("reformuler").catch(() => {});
  await pause(600);
  await selPortee.selectOption("document").catch(() => {});
  await pause(900);

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
      await pause(3600);
    });
  await pause(2200);

  const remplacer = page.getByRole("button", { name: /remplacer/i }).first();
  if (await remplacer.isVisible().catch(() => false)) {
    await soustitre(page, "Décision", "Rien n'est appliqué automatiquement : c'est l'utilisateur qui insère ou remplace.");
    await pause(3200);
    await remplacer.click();
    await pause(2400);
    await soustitre(page, "Résultat", "Le texte retenu remplace le brouillon. L'original reste dans l'historique.");
    await pause(2800);
  }
});

etape("Traçabilité", async (page) => {
  const bouton = page.getByRole("button", { name: /Passages issus/i }).first();
  if (await bouton.isVisible().catch(() => false)) {
    await soustitre(page, "Traçabilité", "L'historique conserve l'action, l'avant, l'après et le nombre de jetons.");
    await bouton.click();
    await pause(3200);
    await page.mouse.wheel(0, 240);
    await soustitre(page, "Traçabilité", "Cette même table sert trois choses : l'historique, le calcul du quota, la preuve RGPD et AI Act.");
    await pause(4200);
    await soustitre(page, "Traçabilité", "L'entrée est écrite AVANT l'appel au modèle, et annulée s'il ne répond pas : un échec ne coûte aucun quota.");
    await pause(4000);
    await page.mouse.wheel(0, -240);
    await pause(600);
  }
});

etape("Terminé, puis export PDF", async (page) => {
  await soustitre(page, "Statut", "Un document passe de brouillon à terminé — et seul un document terminé s'exporte.");
  const statut = page.locator("select").filter({ has: page.locator('option[value="termine"]') }).first();
  if (await statut.isVisible().catch(() => false)) {
    await statut.selectOption("termine").catch(() => {});
    await pause(1600);
  }
  const enregistrer = page.getByRole("button", { name: /enregistrer/i }).first();
  if (await enregistrer.isVisible().catch(() => false)) {
    await enregistrer.click();
    await pause(2600);
  }
  const exporter = page.getByRole("button", { name: /pdf|exporter/i }).first();
  if (await exporter.isVisible().catch(() => false)) {
    await soustitre(page, "Export PDF", "Le PDF est produit côté serveur depuis le même Markdown que l'aperçu — pas un second rendu.");
    await pause(4000);
    await soustitre(page, "Export PDF", "Le serveur refuse par un 409 tout document qui n'est pas terminé : le bouton suit la règle, il ne la remplace pas.");
    await pause(4200);
  } else {
    await soustitre(page, "Export PDF", "Produit côté serveur depuis le même Markdown que l'aperçu — pas un second rendu.");
    await pause(2600);
  }
});

// ─────────────────────────── 4. ce que le serveur refuse ──────────────────────

etape("Quota serveur", async (page) => {
  await deconnexion(page);
  await soustitre(page, "Quota", "Second compte, dont les 20 appels des dernières 24 heures sont déjà consommés.");
  await pause(1100);
  await connexion(page, "karim");

  await page.goto(`${BASE}/documents`, { waitUntil: "networkidle" });
  await pause(1400);
  const liste = await appelApi(page, "/documents");
  const id = liste.corps?.items?.[0]?.id_document;
  docDAutrui = id ?? docDAutrui;      // servira à l'étape suivante, sous un AUTRE compte
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
  await pause(7000);
  await retirerCarte(page);
});

etape("Cloisonnement", async (page) => {
  // Session neuve : la rotation du refresh token invalide le jeton à chaque
  // usage, et deux appels d'API enchaînés dans l'étape précédente ont déjà
  // fait tourner celui-ci. Sans cette reconnexion, la carte afficherait 401
  // — l'application aurait raison, mais la démonstration dirait autre chose.
  await deconnexion(page);
  await connexion(page, "camille");
  await soustitre(page, "Cloisonnement", "On redemande, sous le compte de Camille, un document qui appartient à Karim.");
  await pause(2600);
  const { statut: resultat } = await appelApi(page, `/documents/${docDAutrui}`);
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
  await pause(9500);
  await retirerCarte(page);
});

etape("Back-office", async (page) => {
  await deconnexion(page);
  await connexion(page, "admin");
  await page.goto(`${BASE}/admin`, { waitUntil: "networkidle" });
  await soustitre(page, "Back-office", "Statistiques d'usage, recherche de comptes, et journal des actions d'administration.");
  await pause(3600);
  await page.mouse.wheel(0, 500);
  await pause(3200);
  await page.mouse.wheel(0, 600);
  await soustitre(page, "Back-office", "Le rôle est relu en base à chaque requête — jamais lu dans le jeton.");
  await pause(4200);
  await page.mouse.wheel(0, 600);
  await soustitre(page, "Back-office", "Chaque action d'administration est journalisée : qui, quoi, quand, sur quel compte.");
  await pause(4200);
});

// ─────────────────────────── 5. clôture ───────────────────────────

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
  await pause(11000);
});

await executer(etapes, { sortie: SORTIE, nom: "demo-3min-helpmedraft" });
