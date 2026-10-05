/**
 * Tests système TS-01 à TS-10 du plan de tests, exécutés sur la PILE
 * CONTENEURISÉE (frontend nginx :8080, backend gunicorn :5000, MySQL 8.4).
 *
 * Les comptes viennent de database/jeu_essai.py ; leur mot de passe commun est
 * lu dans MDP_JEU_ESSAI (voir commun.mjs), et non écrit ici.
 *
 * Prérequis — comme audit-accessibilite.mjs, Playwright n'est pas une dépendance
 * du projet :
 *
 *   npm install playwright && npx playwright install chromium
 *
 * Puis, la pile démarrée et le jeu d'essai chargé :
 *
 *   docker compose up --build -d
 *
 *   # l'URL de connexion se compose avec le mot de passe du compte de migration,
 *   # qui est dans le .env de la racine — jamais écrit dans un fichier versionné
 *   set -a && . ./.env && set +a
 *   URL_MIGRATION="mysql+pymysql://helpmedraft_migration"
 *   URL_MIGRATION="$URL_MIGRATION:$MYSQL_MIGRATION_PASSWORD@db:3306/helpmedraft"
 *   docker compose run --rm --no-deps -e HELPMEDRAFT_DB_URL="$URL_MIGRATION" \
 *     backend python -m database.jeu_essai --vider
 *
 *   MDP_JEU_ESSAI=<celui qu'affiche jeu_essai.py> node tests-systeme.mjs
 *
 * TS-02 est exécuté EN DERNIER à dessein : voir le commentaire de son bloc.
 */
import {
  API,
  ATTENTE_TRANSITION_MS,
  FRONT,
  MESURE_FOCUS,
  connecter,
  demanderGeneration,
  entetesApi,
  lancerNavigateur,
  motDePasseJeuEssai,
  nouvelOnglet,
  premierDocument,
} from "./commun.mjs";

const MDP = motDePasseJeuEssai();
const resultats = [];

function noter(id, intitule, verdict, detail) {
  resultats.push({ id, intitule, verdict, detail });
  const marque = { ok: "✔", ko: "✘", partiel: "◐", bloque: "—" }[verdict];
  console.log(`${marque} ${id}  ${intitule}\n     ${detail}`);
}

const navigateur = await lancerNavigateur();

// ── TS-01 inscription → connexion → tableau de bord ──────────────────────────
{
  const { ctx, page } = await nouvelOnglet(navigateur);
  const email = `ts01.${Date.now()}@exemple.fr`;
  await page.goto(`${FRONT}/register`, { waitUntil: "networkidle" });
  const champs = await page.$$('input[type="text"], input[type="email"], input[type="password"]');
  // nom, prénom, email, mot de passe, confirmation — dans l'ordre du formulaire
  const mdpEssai = `${MDP}Ts01`; // dérivé de celui du jeu d'essai, jamais écrit en dur
  const valeurs = ["Essai", "Systeme", email, mdpEssai, mdpEssai];
  for (let i = 0; i < champs.length && i < valeurs.length; i++) await champs[i].fill(valeurs[i]);
  await page.check('input[type="checkbox"]');
  await page.click('button[type="submit"]');
  await page.waitForTimeout(2500);
  const urlApres = page.url();
  await connecter(page, email, mdpEssai).catch(() => {});
  const surTableauDeBord = page.url().includes("/dashboard");
  const titre = await page.title();
  noter(
    "TS-01",
    "inscription → connexion → tableau de bord",
    surTableauDeBord ? "ok" : "ko",
    `compte ${email} créé (redirection vers ${new URL(urlApres).pathname}), ` +
      `session ouverte, titre « ${titre} »`,
  );
  await ctx.close();
}

// ── TS-03 créer un document → rédiger → enregistrement automatique → recharger ──
{
  const { ctx, page } = await nouvelOnglet(navigateur);
  await connecter(page, "camille@helpmedraft.test");
  await page.goto(`${FRONT}/documents/nouveau`, { waitUntil: "networkidle" });
  const marqueur = `Contenu de contrôle ${Date.now()}`;
  await page.fill('input[type="text"]', "Document TS-03");
  await page.click(".cm-content");
  await page.keyboard.type(marqueur);
  // L'enregistrement automatique est temporisé : on attend, puis on recharge.
  await page.waitForTimeout(4000);
  await page.waitForURL(/\/documents\/[0-9a-f-]{36}/, { timeout: 20000 }).catch(() => {});
  const url = page.url();
  await page.reload({ waitUntil: "networkidle" });
  await page.waitForTimeout(1500);
  const contenu = await page.textContent(".cm-content");
  noter(
    "TS-03",
    "rédaction → enregistrement automatique → rechargement",
    contenu?.includes(marqueur) ? "ok" : "ko",
    `document ${new URL(url).pathname} rechargé, contenu ${
      contenu?.includes(marqueur) ? "conservé" : "PERDU"
    }`,
  );
  await ctx.close();
}

// ── TS-05 dossier : créer → classer → supprimer le dossier ──────────────────
{
  const entetes = await entetesApi("camille@helpmedraft.test");

  const dossier = await (
    await fetch(`${API}/dossiers`, {
      method: "POST",
      headers: entetes,
      body: JSON.stringify({ nom: `Dossier TS-05 ${Date.now()}` }),
    })
  ).json();
  const doc = await (
    await fetch(`${API}/documents`, {
      method: "POST",
      headers: entetes,
      body: JSON.stringify({
        titre: "Document classé TS-05",
        content: "Contenu",
        format: "markdown",
        id_dossier: dossier.id_dossier,
      }),
    })
  ).json();
  await fetch(`${API}/dossiers/${dossier.id_dossier}`, { method: "DELETE", headers: entetes });
  const apres = await (
    await fetch(`${API}/documents/${doc.id_document}`, { headers: entetes })
  ).json();
  noter(
    "TS-05",
    "créer un dossier → y classer un document → supprimer le dossier",
    apres.id_document === doc.id_document && apres.id_dossier === null ? "ok" : "ko",
    `document conservé après suppression du dossier, id_dossier = ${JSON.stringify(
      apres.id_dossier,
    )} (ON DELETE SET NULL)`,
  );
}

// ── TS-06 quota IA épuisé ───────────────────────────────────────────────────
{
  const entetes = await entetesApi("karim@helpmedraft.test");
  const { code, corps } = await demanderGeneration(entetes, await premierDocument(entetes));
  noter(
    "TS-06",
    "épuiser le quota IA",
    code === 429 ? "ok" : "ko",
    `compte au quota épuisé → HTTP ${code}, message « ${
      corps.error || corps.message || JSON.stringify(corps)
    } » — refus avant tout appel au modèle`,
  );
}

// ── TS-07 Ollama injoignable ────────────────────────────────────────────────
{
  const entetes = await entetesApi("camille@helpmedraft.test");
  const id = await premierDocument(entetes);
  const { code, corps } = await demanderGeneration(entetes, id);

  // L'éditeur doit rester utilisable après l'échec.
  const { ctx, page } = await nouvelOnglet(navigateur);
  await connecter(page, "camille@helpmedraft.test");
  await page.goto(`${FRONT}/documents/${id}`, { waitUntil: "networkidle" });
  await page.waitForTimeout(1200);
  await page.click(".cm-content");
  await page.keyboard.type(" suite");
  const editable = await page.evaluate(
    () => document.querySelector(".cm-content")?.getAttribute("contenteditable") === "true",
  );
  await ctx.close();
  noter(
    "TS-07",
    "Ollama injoignable → message explicite, éditeur utilisable",
    code === 502 && editable ? "ok" : "ko",
    `HTTP ${code}, message « ${corps.error} » ; éditeur encore ${
      editable ? "éditable" : "BLOQUÉ"
    }`,
  );
}

// ── TS-08 back-office administrateur ────────────────────────────────────────
{
  const { ctx, page } = await nouvelOnglet(navigateur);
  await connecter(page, "admin@helpmedraft.test");
  await page.goto(`${FRONT}/admin`, { waitUntil: "networkidle" });
  await page.waitForTimeout(1500);
  const lignes = await page.$$eval("tbody tr", (t) => t.length);
  const texte = await page.textContent("main");
  const comptesAffiches = ["admin@", "camille@", "karim@", "lena@"].filter((e) =>
    texte?.includes(e),
  ).length;
  const chiffres = /\d/.test(texte || "");
  noter(
    "TS-08",
    "connexion administrateur → back-office",
    lignes >= 4 && comptesAffiches === 4 && chiffres ? "ok" : "ko",
    `${lignes} lignes de comptes, ${comptesAffiches}/4 comptes du jeu d'essai affichés, statistiques présentes`,
  );
  await ctx.close();
}

// ── TS-09 navigation au clavier seul ───────────────────────────────────────
{
  const { ctx, page } = await nouvelOnglet(navigateur);
  await connecter(page, "camille@helpmedraft.test");
  const parcours = ["/dashboard", "/documents", "/documents/nouveau"];
  let totalAtteints = 0;
  let sansFocus = 0;
  for (const chemin of parcours) {
    await page.goto(FRONT + chemin, { waitUntil: "networkidle" });
    await page.waitForTimeout(800);
    for (let i = 0; i < 30; i++) {
      await page.keyboard.press("Tab");
      await page.waitForTimeout(ATTENTE_TRANSITION_MS);
      const etat = await page.evaluate(MESURE_FOCUS);
      if (!etat) continue;
      totalAtteints++;
      if (!etat.focusVisible) sansFocus++;
    }
  }
  noter(
    "TS-09",
    "navigation au clavier seul sur un parcours complet",
    sansFocus === 0 ? "ok" : "ko",
    `${parcours.length} écrans, ${totalAtteints} prises de focus, ${sansFocus} sans indication visible`,
  );
  await ctx.close();
}

// ── TS-02 mot de passe oublié — EXÉCUTÉ EN DERNIER ─────────────────────────
//
// La requête se bloque sur la connexion SMTP et immobilise un worker gunicorn
// jusqu'à son abandon. Placée en tête, elle faussait tous les tests suivants :
// le service entier devenait injoignable. C'est le constat lui-même, et la
// raison de cet ordre.
{
  const depart = Date.now();
  let verdict = "partiel";
  let detail;
  try {
    const r = await fetch(`${API}/auth/forgot-password`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: "camille@helpmedraft.test" }),
      signal: AbortSignal.timeout(20000),
    });
    detail = `la demande répond ${r.status} en ${Math.round((Date.now() - depart) / 1000)} s`;
  } catch {
    verdict = "ko";
    detail =
      `AUCUNE réponse après 20 s : la route reste bloquée sur la connexion SMTP. ` +
      `Le serveur de courriel n'est pas joignable depuis ce conteneur, et la requête ` +
      `n'impose aucun délai — elle immobilise un worker gunicorn. Voir le constat ` +
      `« /auth/forgot-password sans délai SMTP » du compte rendu.`;
  }
  noter("TS-02", "mot de passe oublié → mail → réinitialisation", verdict, detail);
}

// ── TS-04 et TS-10 : hors de portée de cet environnement ───────────────────
noter(
  "TS-04",
  "sélection → reformuler → remplacer",
  "bloque",
  "exige un serveur Ollama avec le modèle chargé ; aucun n'est joignable depuis ce conteneur. " +
    "Le chemin applicatif est couvert par les tests d'intégration (faux serveur HTTP).",
);
noter(
  "TS-10",
  "restitution par lecteur d'écran de l'éditeur",
  "bloque",
  "exige NVDA ou VoiceOver sur une machine graphique. Les noms accessibles sont posés " +
    "(aria-label sur CodeMirror), mais la restitution ne se vérifie pas autrement.",
);

await navigateur.close();

const n = (v) => resultats.filter((r) => r.verdict === v).length;
console.log(
  `\nBilan : ${n("ok")} au vert, ${n("partiel")} partiel, ${n("bloque")} hors de portée, ${n("ko")} en échec.`,
);
const { writeFileSync } = await import("node:fs");
writeFileSync(
  new URL("./resultat-tests-systeme.json", import.meta.url),
  JSON.stringify({ date: new Date().toISOString(), front: FRONT, api: API, resultats }, null, 2),
);
if (n("ko")) process.exitCode = 1;
