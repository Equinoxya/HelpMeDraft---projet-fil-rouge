// Support de soutenance CDA — HelpMeDraft
// Contenu repris du dossier projet (docs/Dossier-projet-HelpMeDraft.pdf) pour
// qu'aucune affirmation du diaporama ne contredise ce que le jury a lu.

const pptxgen = require("pptxgenjs");
const { applyTheme } = require("/root/.claude/skills/synced/c1c8c12f-8277-41a7-a992-cea745916b4e_fa19c528-ebca-4d79-893f-2c00c15e48d4/pptx/scripts/apply_theme.js");

const R = "/home/user/HelpMeDraft---projet-fil-rouge";
const OUT = process.argv[2] || "Soutenance-HelpMeDraft.pptx";

const THEME = {
  name: "HelpMeDraft",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1B2033",
    lt1: "FFFFFF",
    dk2: "141B2D",
    lt2: "EDEFF4",
    accent1: "D98324", // ocre — accent principal
    accent2: "1B2A41", // encre
    accent3: "2A9D8F", // vert — acquis
    accent4: "B3261E", // rouge — risque
    accent5: "5B6880", // gris sur fond clair
    accent6: "9AA8C0", // gris sur fond sombre
    hlink: "D98324",
    folHlink: "5B6880",
  },
};

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.3 x 7.5
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.author = "Ophélie Bellissens";
pres.title = "HelpMeDraft — soutenance CDA";
pres.subject = "Dossier projet CDA — HelpMeDraft";

const C = pres.SchemeColor;
const W = 13.3, H = 7.5, M = 0.6, CW = W - 2 * M; // 12.1

const FOOT = "HelpMeDraft  ·  Ophélie Bellissens  ·  CDA — Metz Numeric School";
const shadow = (o = {}) => ({ type: "outer", angle: 90, blur: 10, offset: 2, color: "0E1422", opacity: 0.12, ...o });

// ───────────────────────────── layouts ─────────────────────────────

const footLight = [
  { text: { text: FOOT, options: { x: M, y: 6.98, w: 8, h: 0.3, fontSize: 9, color: THEME.colors.accent5, isTextBox: true, objectName: "pied" } } },
];
const footDark = [
  { text: { text: FOOT, options: { x: M, y: 6.98, w: 8, h: 0.3, fontSize: 9, color: THEME.colors.accent6, isTextBox: true, objectName: "pied" } } },
];
const numLight = { x: 12.5, y: 6.98, w: 0.4, h: 0.3, fontSize: 9, color: THEME.colors.accent5, align: "right" };
const numDark = { x: 12.5, y: 6.98, w: 0.4, h: 0.3, fontSize: 9, color: THEME.colors.accent6, align: "right" };

pres.defineSlideMaster({
  title: "TITLE",
  background: { color: C.text2 },
  objects: [
    { placeholder: { options: { name: "kicker", type: "body", x: M + 0.3, y: 1.9, w: CW, h: 0.4, fontSize: 14, color: C.accent1, bold: true, charSpacing: 2 }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", align: "left", x: M + 0.3, y: 2.4, w: 11.6, h: 1.5, fontSize: 44, bold: true, color: C.background1, valign: "top" }, text: "" } },
    { placeholder: { options: { name: "subtitle", type: "body", x: M + 0.3, y: 3.95, w: 11.0, h: 0.9, fontSize: 19, color: C.accent6 }, text: "" } },
    { placeholder: { options: { name: "meta", type: "body", x: M + 0.3, y: 5.5, w: 11.0, h: 1.0, fontSize: 14, color: C.accent6 }, text: "" } },
  ],
});

pres.defineSlideMaster({
  title: "SECTION",
  background: { color: C.text2 },
  objects: [
    { placeholder: { options: { name: "num", type: "body", x: M + 0.3, y: 2.0, w: 2.2, h: 1.6, fontSize: 80, bold: true, color: C.accent1, valign: "bottom" }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", align: "left", x: M + 0.3, y: 3.7, w: 11.6, h: 1.0, fontSize: 34, bold: true, color: C.background1, valign: "top" }, text: "" } },
    { placeholder: { options: { name: "sub", type: "body", x: M + 0.3, y: 4.7, w: 11.0, h: 0.5, fontSize: 15, color: C.accent6 }, text: "" } },
  ],
  slideNumber: numDark,
});

pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: C.background1 },
  objects: [
    ...footLight,
    { placeholder: { options: { name: "title", type: "title", align: "left", x: M, y: 0.42, w: CW, h: 0.9, fontSize: 30, bold: true, color: C.text1, valign: "bottom" }, text: "" } },
    { placeholder: { options: { name: "lead", type: "body", x: M, y: 1.38, w: CW, h: 0.42, fontSize: 14, color: C.accent5 }, text: "" } },
  ],
  slideNumber: numLight,
});

pres.defineSlideMaster({
  title: "MEDIA",
  background: { color: C.background1 },
  objects: [
    ...footLight,
    { placeholder: { options: { name: "title", type: "title", align: "left", x: M, y: 0.42, w: CW, h: 0.9, fontSize: 30, bold: true, color: C.text1, valign: "bottom" }, text: "" } },
    { placeholder: { options: { name: "caption", type: "body", x: M, y: 6.52, w: CW, h: 0.35, fontSize: 11, color: C.accent5, italic: true }, text: "" } },
  ],
  slideNumber: numLight,
});

pres.defineSlideMaster({
  title: "SPLIT",
  background: { color: C.background1 },
  objects: [
    ...footLight,
    { placeholder: { options: { name: "title", type: "title", align: "left", x: M, y: 0.42, w: CW, h: 0.9, fontSize: 30, bold: true, color: C.text1, valign: "bottom" }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: M, y: 1.5, w: 6.1, h: 4.9, fontSize: 15, color: C.text1, valign: "top" }, text: "" } },
    { placeholder: { options: { name: "caption", type: "body", x: 7.0, y: 6.52, w: 5.7, h: 0.35, fontSize: 11, color: C.accent5, italic: true, align: "center" }, text: "" } },
  ],
  slideNumber: numLight,
});

pres.defineSlideMaster({
  title: "CLOSE",
  background: { color: C.text2 },
  objects: [
    ...footDark,
    { placeholder: { options: { name: "title", type: "title", align: "left", x: M, y: 0.6, w: CW, h: 0.9, fontSize: 32, bold: true, color: C.background1, valign: "bottom" }, text: "" } },
  ],
  slideNumber: numDark,
});

// ───────────────────────────── helpers ─────────────────────────────

let n = 0;
function add(masterName, sectionTitle, notes) {
  n += 1;
  const s = pres.addSlide({ masterName, sectionTitle });
  if (notes) s.addNotes(notes);
  return s;
}

// carte : fond teinté, pastille ocre numérotée, titre, corps
function card(s, { x, y, w, h, badge, title, body, accent }) {
  const col = accent || C.accent1;
  s.addShape(pres.ShapeType.roundRect, {
    x, y, w, h, rectRadius: 0.08, fill: { color: C.background2 },
    line: { color: C.background2 }, shadow: shadow(), objectName: `carte ${title}`,
  });
  let tx = x + 0.28;
  if (badge) {
    s.addShape(pres.ShapeType.ellipse, { x: x + 0.28, y: y + 0.26, w: 0.42, h: 0.42, fill: { color: col }, line: { color: col }, objectName: `pastille ${badge}` });
    s.addText(badge, { x: x + 0.28, y: y + 0.26, w: 0.42, h: 0.42, fontSize: 13, bold: true, color: "FFFFFF", align: "center", valign: "middle", margin: 0, isTextBox: true });
    tx = x + 0.86;
  }
  s.addText(title, { x: tx, y: y + 0.24, w: x + w - 0.28 - tx, h: 0.46, fontSize: 15, bold: true, color: C.text1, valign: "middle", margin: 0, isTextBox: true });
  if (body) {
    s.addText(body, { x: x + 0.28, y: y + 0.78, w: w - 0.56, h: h - 1.02, fontSize: 14, color: C.text1, valign: "top", margin: 0, lineSpacing: 19, isTextBox: true });
  }
}

// tuile de chiffre
function stat(s, { x, y, w, h, value, label }) {
  s.addShape(pres.ShapeType.roundRect, {
    x, y, w, h, rectRadius: 0.08, fill: { color: C.background2 },
    line: { color: C.background2 }, shadow: shadow(), objectName: `chiffre ${value}`,
  });
  s.addText(value, { x: x + 0.2, y: y + 0.12, w: w - 0.4, h: 0.62, fontSize: 34, bold: true, color: C.accent1, align: "center", valign: "middle", margin: 0, isTextBox: true });
  s.addText(label, { x: x + 0.2, y: y + 0.72, w: w - 0.4, h: h - 0.86, fontSize: 13, color: C.text1, align: "center", valign: "top", margin: 0, isTextBox: true });
}

// bloc de code sur fond sombre
function code(s, { x, y, w, h, lines, file, size = 11.5 }) {
  s.addShape(pres.ShapeType.roundRect, {
    x, y, w, h, rectRadius: 0.06, fill: { color: C.text2 }, line: { color: C.text2 },
    shadow: shadow({ opacity: 0.2 }), objectName: `code ${file || ""}`,
  });
  if (file) {
    s.addText(file, { x: x + 0.3, y: y + 0.16, w: w - 0.6, h: 0.28, fontSize: 10.5, color: THEME.colors.accent1, fontFace: "Courier New", margin: 0, isTextBox: true });
  }
  s.addText(lines.join("\n"), {
    x: x + 0.3, y: y + (file ? 0.5 : 0.24), w: w - 0.6, h: h - (file ? 0.74 : 0.48),
    fontSize: size, fontFace: "Courier New", color: "E6EBF5", lineSpacing: size * 1.5,
    valign: "top", margin: 0, isTextBox: true,
  });
}

// image ajustée dans une zone
function media(s, { file, ratio, x = M, y = 1.5, maxW = CW, maxH = 4.85, name }) {
  let w = Math.min(maxW, maxH * ratio);
  let h = w / ratio;
  const px = x + (maxW - w) / 2;
  const py = y + (maxH - h) / 2;
  s.addImage({ path: file, x: px, y: py, w, h, shadow: shadow({ blur: 14, offset: 3, opacity: 0.18 }), objectName: name || "figure" });
}

const li = (items) => items.map((t, i) => ({
  text: t, options: { bullet: true, breakLine: i < items.length - 1, paraSpaceAfter: 9 },
}));

// ═══════════════════════════ 1. Ouverture ═══════════════════════════

pres.addSection({ title: "Ouverture" });

{
  const s = add("TITLE", "Ouverture",
`[0:00 — 0:30]
Bonjour, je m'appelle Ophélie Bellissens, je suis candidate au titre Concepteur Développeur d'Applications.
Je vais vous présenter HelpMeDraft, une application web de rédaction assistée par IA que j'ai conçue et développée seule, du cahier des charges au déploiement, pour un commanditaire fictif : LexiCorp.
Le dossier que vous avez entre les mains décrit le projet en détail ; cette présentation en suit le fil et s'arrête sur les décisions qui me paraissent les plus défendables — et sur celles que j'ai dû corriger.
Je vous propose quarante minutes, et je garde les questions pour la fin.`);
  s.addText("DOSSIER PROJET CDA", { placeholder: "kicker" });
  s.addText("HelpMeDraft", { placeholder: "title" });
  s.addText("Assistant de rédaction professionnelle assistée par IA, à inférence locale", { placeholder: "subtitle" });
  s.addText("Ophélie Bellissens  ·  Metz Numeric School  ·  Octobre 2026\nCommanditaire : LexiCorp (contexte de formation)", { placeholder: "meta" });
}

{
  const s = add("CONTENT", "Ouverture",
`[0:30 — 1:00]
Six temps. Je commence par le besoin, parce que toutes les décisions techniques qui suivent en découlent.
Puis la gestion de projet, la conception, la réalisation avec du code, la sécurité — qui est le fil rouge du projet — et je termine par les tests, la veille et le bilan.
Annoncez le plan et respectez-le : le jury suit le dossier en parallèle, la correspondance l'aide.`);
  s.addText("Déroulé", { placeholder: "title" });
  s.addText("Six temps, quarante minutes. Les numéros renvoient aux sections du dossier.", { placeholder: "lead" });

  const items = [
    ["1", "Le contexte et le besoin", "Dossier § 2 et § 3", "≈ 4 min"],
    ["2", "La gestion de projet", "§ 4", "≈ 5 min"],
    ["3", "La conception", "§ 5", "≈ 11 min"],
    ["4", "La réalisation", "§ 6 et § 7", "≈ 7 min"],
    ["5", "La sécurité", "§ 8", "≈ 5 min"],
    ["6", "Tests, veille et bilan", "§ 9, § 10, § 11", "≈ 8 min"],
  ];
  items.forEach((it, i) => {
    const y = 1.95 + i * 0.8;
    s.addShape(pres.ShapeType.ellipse, { x: M + 0.1, y: y + 0.08, w: 0.46, h: 0.46, fill: { color: C.accent1 }, line: { color: C.accent1 }, objectName: `puce ${it[0]}` });
    s.addText(it[0], { x: M + 0.1, y: y + 0.08, w: 0.46, h: 0.46, fontSize: 14, bold: true, color: "FFFFFF", align: "center", valign: "middle", margin: 0, isTextBox: true });
    s.addText(it[1], { x: M + 0.85, y: y, w: 6.4, h: 0.62, fontSize: 19, bold: true, color: C.text1, valign: "middle", margin: 0, isTextBox: true });
    s.addText(it[2], { x: 7.4, y: y, w: 2.6, h: 0.62, fontSize: 14, color: C.accent5, valign: "middle", margin: 0, isTextBox: true });
    s.addText(it[3], { x: 10.2, y: y, w: 2.5, h: 0.62, fontSize: 14, color: C.accent1, bold: true, align: "right", valign: "middle", margin: 0, isTextBox: true });
  });
}

// ═══════════════════════════ 2. Besoin ═══════════════════════════

pres.addSection({ title: "Contexte et besoin" });

{
  const s = add("SECTION", "Contexte et besoin",
`[1:00 — 1:10]
Transition courte. « Premier temps : d'où vient la demande. »`);
  s.addText("1", { placeholder: "num" });
  s.addText("Le contexte et le besoin", { placeholder: "title" });
  s.addText("Dossier § 2 — le cahier des charges  ·  § 3 — l'entreprise et le service", { placeholder: "sub" });
}

{
  const s = add("CONTENT", "Contexte et besoin",
`[1:10 — 2:40]
LexiCorp édite des outils de gestion documentaire pour les PME. Son catalogue sait classer et retrouver des documents ; il ne sait pas aider à les écrire.
Le constat de départ est banal et c'est ce qui en fait la force : dans une PME, les courriels clients, les notes internes, les comptes rendus sont rédigés par des gens dont ce n'est pas le métier. Le temps passé est réel, la qualité est inégale, les textes sont repris plusieurs fois.
D'où la commande : une application web qui assiste la rédaction avec un modèle de langage, dans un espace personnel sécurisé. Pour LexiCorp, c'est un déplacement de positionnement : passer de l'organisation des documents à l'assistance à leur production.
Le cahier des charges fixe quatre objectifs. Retenez surtout le quatrième : la sécurité, l'accessibilité et la confidentialité ne sont pas des options en fin de projet, elles sont dans les objectifs. C'est ce qui m'a conduite à l'arbitrage que je présenterai sur l'inférence locale.
Un mot sur mon positionnement : j'étais seule sur toute la chaîne — analyse, conception, front, back, base de données, sécurisation, documentation. Ça a orienté deux choix : une architecture volontairement lisible, et une documentation écrite au fil de l'eau.`);
  s.addText("Aider à écrire, pas seulement à classer", { placeholder: "title" });
  s.addText("LexiCorp, éditeur d'outils de gestion documentaire pour les PME, ouvre un nouveau service.", { placeholder: "lead" });

  card(s, { x: M, y: 1.95, w: 3.87, h: 2.55, badge: "1", title: "Le constat",
    body: "Dans une PME, les écrits courants — courriels, notes, comptes rendus — mobilisent des collaborateurs qui ne sont pas rédacteurs. Qualité inégale, reprises multiples." });
  card(s, { x: M + 4.11, y: 1.95, w: 3.87, h: 2.55, badge: "2", title: "La demande",
    body: "Une application web qui assiste la rédaction à l'aide d'une IA générative, dans un espace personnel sécurisé." });
  card(s, { x: M + 8.22, y: 1.95, w: 3.88, h: 2.55, badge: "3", title: "Mon rôle",
    body: "Conceptrice développeuse full-stack, seule sur la chaîne : analyse, conception, front, back, base de données, sécurisation, documentation." });

  s.addText("Les quatre objectifs du cahier des charges", { x: M, y: 4.85, w: CW, h: 0.4, fontSize: 17, bold: true, color: C.text1, margin: 0, isTextBox: true });
  const obj = [
    ["Rédiger et stocker", "ses documents professionnels"],
    ["Suggérer et reformuler", "via un modèle de langage"],
    ["Un espace sécurisé", "authentification et historique"],
    ["Se conformer", "RGPD, ANSSI, RGAA"],
  ];
  obj.forEach((o, i) => {
    const x = M + i * 3.08;
    s.addText(o[0], { x, y: 5.4, w: 2.9, h: 0.36, fontSize: 16, bold: true, color: C.accent1, margin: 0, isTextBox: true });
    s.addText(o[1], { x, y: 5.78, w: 2.9, h: 0.6, fontSize: 15, color: C.text1, margin: 0, isTextBox: true });
  });
}

{
  const s = add("CONTENT", "Contexte et besoin",
`[2:40 — 4:10]
Le périmètre fonctionnel tient en cinq blocs. Trois commandes IA et trois seulement — reformuler, corriger, compléter — applicables à une sélection ou au document entier, et c'est toujours l'utilisateur qui décide d'insérer ou de remplacer.
Le quota de vingt requêtes par jour vient du cahier des charges ; je l'ai implémenté côté serveur, j'y reviens.
À droite, les exigences non fonctionnelles. La ligne RGPD est celle qui a le plus pesé sur l'architecture : « aucune donnée personnelle transmise à OpenAI sans anonymisation ». Sur des textes rédigés librement, l'anonymisation ne peut jamais être exhaustive — c'est le point de départ de mon choix d'inférence locale.
En bas : ce que j'ai écarté. Le dire explicitement fait partie du travail d'analyse ; un périmètre qu'on ne borne pas est un périmètre qui dérive.
Dernier point, et il est important pour la suite : les obligations de transparence de l'AI Act sont entrées en application le 2 août 2026, après la rédaction du cahier des charges. C'est ma veille qui l'a fait remonter.`);
  s.addText("Périmètre et exigences", { placeholder: "title" });
  s.addText("Cinq blocs fonctionnels, quatre domaines d'exigences, et des limites assumées.", { placeholder: "lead" });

  card(s, { x: M, y: 1.95, w: 5.95, h: 3.75, badge: "a—e", title: "Périmètre fonctionnel",
    body: "Gestion utilisateur — inscription, connexion, mot de passe oublié, deux rôles\nÉditeur Markdown et trois commandes IA : reformuler, corriger, compléter\nGestion documentaire — CRUD, dossiers, enregistrement automatique, historique IA\nIntégration IA — appels serveur, prompt engineering, affichage différencié\nBack-office — comptes, statistiques, quota de 20 requêtes / 24 h" });

  card(s, { x: M + 6.15, y: 1.95, w: 5.95, h: 3.75, badge: "NF", title: "Exigences non fonctionnelles",
    body: "Sécurité — hachage, JWT, protection XSS / CSRF / injections\nAccessibilité — RGAA 4.1.2, contrastes, clavier, ARIA\nRGPD — consentement explicite, aucune donnée transmise à un tiers\nÉco-conception — chargement différé, dépendances limitées, compression\nAI Act — transparence, applicable depuis le 2 août 2026 (hors cahier des charges)" });

  s.addText([
    { text: "Hors périmètre, assumé :  ", options: { bold: true, color: THEME.colors.accent5 } },
    { text: "facturation et abonnements · collaboratif temps réel · application mobile native · export bureautique propriétaire · hébergement cloud de production.", options: { color: THEME.colors.accent5 } },
  ], { x: M, y: 6.0, w: CW, h: 0.6, fontSize: 14, margin: 0, isTextBox: true, objectName: "hors perimetre" });
}

// ═══════════════════════════ 3. Gestion de projet ═══════════════════════════

pres.addSection({ title: "Gestion de projet" });

{
  const s = add("SECTION", "Gestion de projet",
`[4:10 — 4:20]
« Deuxième temps : comment j'ai conduit le projet. »`);
  s.addText("2", { placeholder: "num" });
  s.addText("La gestion de projet", { placeholder: "title" });
  s.addText("Dossier § 4 — méthode, planning, versions, arbitrages", { placeholder: "sub" });
}

{
  const s = add("MEDIA", "Gestion de projet",
`[4:20 — 6:20]
J'ai travaillé en itérations d'une semaine, chacune close par un lot utilisable de bout en bout.
Le point de méthode est le découpage : des lots verticaux — une fonctionnalité qui traverse le front, l'API et la base — plutôt que des couches horizontales. Avec des couches horizontales, on ne valide rien avant l'assemblage final ; avec des lots verticaux, chaque fin d'itération produit quelque chose de démontrable.
Le planning reprend celui du cahier des charges. Tout est terminé sauf trois choses, que j'assume et qui sont écrites dans le dossier : le déploiement effectif, la bascule complète vers MySQL — le schéma est exécuté et vérifié, il me manque une machine avec un démon Docker — et la mention de transparence AI Act.
Sur la gestion de versions : une branche par fonctionnalité, des commits conventionnés, le .env ignoré. Et le package-lock.json commité — ce n'est pas un détail d'organisation, c'est une mesure de sécurité, et la compromission d'axios que je présenterai en fin d'exposé montre pourquoi.
Travaillant seule, j'ai remplacé les rituels d'équipe par un point hebdomadaire avec mon référent et des revues croisées avec la promotion sur la chaîne d'authentification.`);
  s.addText("Des lots verticaux, pas des couches horizontales", { placeholder: "title" });

  stat(s, { x: M, y: 1.42, w: 2.9, h: 1.25, value: "1 semaine", label: "durée d'une itération" });
  stat(s, { x: M + 3.07, y: 1.42, w: 2.9, h: 1.25, value: "6 / 6", label: "étapes du plan engagées" });
  stat(s, { x: M + 6.14, y: 1.42, w: 2.9, h: 1.25, value: "13", label: "lots fonctionnels terminés" });
  stat(s, { x: M + 9.21, y: 1.42, w: 2.89, h: 1.25, value: "3", label: "points restants, documentés" });

  media(s, { file: `${R}/docs/conception/diagrammes/planning-initial-gantt.png`, ratio: 2.48, y: 2.95, maxH: 3.4, name: "planning initial" });
  s.addText("Planning initial repris du cahier des charges et découpé en lots verticaux.", { placeholder: "caption" });
}

{
  const s = add("CONTENT", "Gestion de projet",
`[6:20 — 8:50]
Trois arbitrages résument le projet.
Le premier : un JWT seul ne se révoque pas. J'ai donc ajouté une table user_session côté serveur et une rotation des refresh tokens. Chaque usage invalide le précédent ; si un jeton déjà consommé revient, c'est qu'il a été volé, et toutes les sessions du compte sont révoquées.
Le deuxième : le quota. Je le calcule par agrégation sur le journal des appels IA, pas avec un compteur stocké sur l'utilisateur. Un compteur peut se désynchroniser ; une agrégation, non. Et l'historique reste auditable, ce qui sert aussi la traçabilité RGPD.
Le troisième est le plus structurant : la confidentialité. Plutôt que d'anonymiser des textes libres — ce qui n'est jamais exhaustif —, j'héberge le modèle en local avec Ollama. L'exigence est satisfaite par construction. Les contreparties sont réelles et je les assume : plus de latence, une qualité inférieure à GPT-4, un prérequis d'installation, et un service de plus à maintenir. Ma veille l'a confirmé : une CVE critique sur Ollama en avril.
La quatrième carte est un échec que j'ai choisi de garder dans le dossier. Mes textes d'interface avaient dérivé vers un positionnement « juridique » que le cahier des charges ne demande pas. Vingt libellés dans neuf fichiers. Le dernier résidu n'était pas dans l'interface : il était dans les gabarits de prompt du backend — « Tu es un assistant de rédaction juridique ». Invisible, mais envoyé au modèle à chaque appel, donc avec un effet réel sur les sorties. J'en tire une règle : un prompt est du code, et il se teste comme du code. C'est le cas de test TU-04.`);
  s.addText("Trois arbitrages, et une erreur corrigée", { placeholder: "title" });
  s.addText("Les décisions que je défends, et celle que j'ai dû reprendre.", { placeholder: "lead" });

  card(s, { x: M, y: 1.95, w: 3.87, h: 2.5, badge: "1", title: "Session révocable",
    body: "Un JWT seul ne se révoque pas. Table user_session + rotation des refresh tokens : rejouer un jeton consommé est traité comme un vol." });
  card(s, { x: M + 4.11, y: 1.95, w: 3.87, h: 2.5, badge: "2", title: "Quota par agrégation",
    body: "Comptage sur le journal des appels, pas un compteur sur l'utilisateur : la valeur ne peut pas se désynchroniser et l'historique reste auditable." });
  card(s, { x: M + 8.22, y: 1.95, w: 3.88, h: 2.5, badge: "3", title: "Confidentialité",
    body: "Inférence locale : les contenus ne quittent pas l'infrastructure. Contreparties assumées — latence, qualité, maintenance." });

  card(s, { x: M, y: 4.68, w: 12.1, h: 1.6, badge: "!", accent: THEME.colors.accent4, title: "L'erreur : une dérive du positionnement éditorial",
    body: "Vingt libellés avaient glissé vers un positionnement « juridique » absent du cahier des charges. Le dernier résidu n'était pas visible : les gabarits de prompt du backend. Invisibles, mais envoyés au modèle à chaque appel — donc avec un effet réel. Un prompt est du code : il se teste comme du code (cas TU-04)." });
}

// ═══════════════════════════ 4. Conception ═══════════════════════════

pres.addSection({ title: "Conception" });

{
  const s = add("SECTION", "Conception",
`[8:50 — 9:00]
« Troisième temps, le plus long : la conception. »`);
  s.addText("3", { placeholder: "num" });
  s.addText("La conception", { placeholder: "title" });
  s.addText("Dossier § 5 — architecture, maquettes, modèle de données, cas d'utilisation", { placeholder: "sub" });
}

{
  const s = add("MEDIA", "Conception",
`[9:00 — 11:30]
Architecture client/serveur découplée en trois niveaux, avec un service d'inférence en périphérie.
Le point à retenir est celui du titre : le navigateur ne dialogue jamais directement avec le moteur d'inférence. Tout passe par l'API, qui vérifie l'authentification, la propriété du document, le quota, puis journalise l'interaction.
Si le front appelait Ollama directement, ni le quota ni la traçabilité RGPD ne seraient applicables — un utilisateur contournerait le quota en appelant le port 11434 lui-même. L'intermédiaire n'est pas une commodité, c'est ce qui rend les contraintes du cahier des charges opposables.
Deuxième point : le moteur n'écoute que sur l'interface de bouclage. C'était une habitude implicite ; c'est devenu une consigne écrite après la publication de la CVE sur Ollama.
Deux écarts à la recommandation du cahier des charges, tous deux argumentés dans le dossier. Vue 3 plutôt que React : le cahier des charges recommande sans imposer, et une meilleure maîtrise réduit le risque sur un projet mené seule. Ollama plutôt qu'OpenAI : le cahier des charges autorise explicitement les deux, et c'est l'exigence RGPD qui tranche.`);
  s.addText("Le navigateur ne parle jamais au moteur d'inférence", { placeholder: "title" });
  media(s, { file: `${R}/docs/dossier/fig/archi.png`, ratio: 2.28, y: 1.45, maxH: 4.9, name: "architecture" });
  s.addText("Architecture logicielle — trois niveaux et services périphériques (dossier § 5.2).", { placeholder: "caption" });
}

{
  const s = add("CONTENT", "Conception",
`[11:30 — 13:30]
Le backend est découpé en trois couches, et la règle qui compte est celle de la colonne de droite : ce que chaque couche ne contient jamais.
Aucun import Flask dans services/. Cette règle n'est pas esthétique, elle est fonctionnelle : c'est elle qui rend les composants métier testables sans démarrer de serveur ni ouvrir de base. Sans elle, tout test d'auth_service ou d'ia_service deviendrait un test d'intégration, plus lent et plus fragile. C'est le socle du plan de tests.
Je suis honnête sur une nuance, et elle est écrite dans le dossier : la lecture de la configuration passe par current_app, qui est un objet Flask. C'est le seul point où la règle fléchit, et le dossier l'explique en § 7.2.
Cinq blueprints structurent l'API : auth, documents, dossiers, IA, admin.
Côté front, la même logique : aucune vue n'appelle axios directement, tout passe par la couche services. L'intercepteur qui rafraîchit l'access token après un 401 et rejoue la requête est donc écrit une seule fois, à un seul endroit.`);
  s.addText("Aucun import Flask dans services/", { placeholder: "title" });
  s.addText("La règle d'architecture qui rend le plan de tests possible.", { placeholder: "lead" });

  const rows = [
    ["Présentation", "app/routes/", "Validation des entrées, codes de retour, sérialisation JSON", "Règle métier"],
    ["Métier", "app/services/", "Hachage, cycle de vie des jetons, prompts, appel au modèle, courriels", "Flask : request, response"],
    ["Persistance", "database/db.py", "Modèles SQLAlchemy, relations, contraintes, requêtes et agrégations", "Logique de présentation"],
  ];
  s.addText("Couche", { x: M + 0.28, y: 1.95, w: 1.9, h: 0.3, fontSize: 12, bold: true, color: THEME.colors.accent5, margin: 0, isTextBox: true });
  s.addText("Responsabilité", { x: M + 4.0, y: 1.95, w: 4.4, h: 0.3, fontSize: 12, bold: true, color: THEME.colors.accent5, margin: 0, isTextBox: true });
  s.addText("Ne contient jamais", { x: M + 8.7, y: 1.95, w: 3.1, h: 0.3, fontSize: 12, bold: true, color: THEME.colors.accent4, margin: 0, isTextBox: true });
  rows.forEach((r, i) => {
    const y = 2.3 + i * 1.12;
    s.addShape(pres.ShapeType.roundRect, { x: M, y, w: CW, h: 1.0, rectRadius: 0.06, fill: { color: C.background2 }, line: { color: C.background2 }, shadow: shadow(), objectName: `couche ${r[0]}` });
    s.addText(r[0], { x: M + 0.28, y: y + 0.14, w: 3.5, h: 0.34, fontSize: 15, bold: true, color: C.text1, margin: 0, isTextBox: true });
    s.addText(r[1], { x: M + 0.28, y: y + 0.5, w: 3.5, h: 0.34, fontSize: 12.5, color: THEME.colors.accent5, fontFace: "Courier New", margin: 0, isTextBox: true });
    s.addText(r[2], { x: M + 4.0, y: y + 0.14, w: 4.5, h: 0.75, fontSize: 14, color: C.text1, margin: 0, isTextBox: true });
    s.addText(r[3], { x: M + 8.7, y: y + 0.14, w: 3.1, h: 0.75, fontSize: 14, color: THEME.colors.accent4, margin: 0, isTextBox: true });
  });
  s.addText("Côté front, la même règle : aucune vue n'appelle axios. L'intercepteur qui rejoue une requête après un 401 est donc écrit une seule fois.",
    { x: M, y: 5.85, w: CW, h: 0.5, fontSize: 13.5, color: THEME.colors.accent5, margin: 0, isTextBox: true, objectName: "note front" });
}

{
  const s = add("MEDIA", "Conception",
`[13:30 — 15:00]
Neuf planches de maquettage, une par écran, construites en trois temps : recensement des écrans à partir du périmètre, charte graphique et composants, puis les planches elles-mêmes.
Celle-ci est l'écran le plus représentatif du produit : l'éditeur. Chaque planche porte sa route, sa garde de routeur, et une colonne « intentions » numérotée qui explique pourquoi l'écran est fait comme ça.
Deux intentions à relever ici. La quatrième : l'enregistrement automatique 2,5 secondes après la dernière frappe, doublé d'un bouton explicite — je montrerai le code. La cinquième : l'historique des interactions IA, avec l'action, l'avant, l'après et le nombre de tokens. Ce n'est pas un confort, c'est la traçabilité exigée par le cahier des charges.
Le maquettage a servi deux objectifs : vérifier la couverture du périmètre, et fixer les intentions avant d'écrire la moindre ligne de Vue.`);
  s.addText("Neuf planches, une intention par écran", { placeholder: "title" });
  media(s, { file: `${R}/docs/dossier/fig/planches/image6.png`, ratio: 1.88, y: 1.45, maxH: 4.9, name: "planche W-06" });
  s.addText("Planche W-06 — éditeur de document, l'écran le plus représentatif (dossier § 5.3, § 12.1).", { placeholder: "caption" });
}

{
  const s = add("MEDIA", "Conception",
`[15:00 — 16:00]
L'enchaînement des écrans. Trois zones : le public, l'espace authentifié, le back-office.
Le routeur applique trois gardes qui correspondent exactement à ces zones : guest pour les pages de connexion et d'inscription, auth pour l'espace personnel, admin pour le back-office.
Je précise tout de suite, parce que c'est la question qu'on pose : ces gardes sont du confort d'usage. Elles évitent d'afficher un écran vide et masquent le menu d'administration. Le contrôle qui compte est côté serveur, et je le montrerai dans la partie sécurité.`);
  s.addText("Trois zones, trois gardes de routeur", { placeholder: "title" });
  media(s, { file: `${R}/docs/conception/diagrammes/enchainement-ecrans.png`, ratio: 1.45, y: 1.45, maxH: 4.9, name: "enchainement des ecrans" });
  s.addText("Enchaînement des écrans et gardes du routeur (dossier § 5.3).", { placeholder: "caption" });
}

{
  const s = add("MEDIA", "Conception",
`[16:00 — 18:30]
Le modèle entités-associations. Sept tables.
Trois choix à défendre.
Les identifiants sont des UUID v4, pas des entiers auto-incrémentés. Conséquence directe sur la sécurité : les identifiants ne sont pas énumérables. On ne balaie pas /documents/1, /documents/2.
Les cascades sont déclarées au niveau du SGBD, pas seulement dans l'ORM. Si quelqu'un supprime une ligne avec un client SQL, l'intégrité tient quand même. Une contrainte qui n'existe que dans le code applicatif n'est pas une contrainte.
La table ia journalise chaque interaction avec le contenu avant et après. Elle sert trois choses à la fois : l'historique affiché dans l'éditeur, le calcul du quota par agrégation, et la traçabilité RGPD. C'est la même donnée qui rend les trois possibles.
Le modèle logique et le modèle physique sont dans le dossier en § 5.4, et le script de création MySQL en § 5.5 — il a été exécuté et vérifié sur un serveur réel.`);
  s.addText("Sept tables, des UUID, des cascades côté SGBD", { placeholder: "title" });
  media(s, { file: `${R}/docs/dossier/fig/mcd.png`, ratio: 2.04, y: 1.45, maxH: 4.9, name: "modele entites-associations" });
  s.addText("Modèle entités-associations (dossier § 5.4) ; modèle physique et script MySQL en § 5.4 et § 5.5.", { placeholder: "caption" });
}

{
  const s = add("MEDIA", "Conception",
`[18:30 — 19:30]
Trois acteurs : le visiteur, l'utilisateur authentifié, l'administrateur.
Le périmètre de l'utilisateur est strictement limité à ses propres documents et dossiers, ses trois actions IA dans la limite de son quota, et son historique. L'administrateur hérite de tout le périmètre utilisateur et ajoute le back-office.
Le moteur d'inférence apparaît comme un système externe sollicité par l'API — jamais par le navigateur, c'est la cohérence avec l'architecture.
Le cas le plus significatif est la génération d'une assistance IA : c'est celui que je détaille en diagramme de séquence, et c'est aussi celui sur lequel porte mon jeu d'essai.`);
  s.addText("Trois acteurs, un périmètre cloisonné", { placeholder: "title" });
  media(s, { file: `${R}/docs/dossier/fig/usecase.png`, ratio: 1.37, y: 1.45, maxH: 4.9, name: "cas d'utilisation" });
  s.addText("Diagramme des cas d'utilisation (dossier § 5.6).", { placeholder: "caption" });
}

{
  const s = add("MEDIA", "Conception",
`[19:30 — 21:30]
Le diagramme de séquence du cas le plus significatif : la génération d'une assistance IA.
Suivez l'ordre des contrôles, il n'est pas arbitraire. Authentification, puis propriété du document, puis validation des entrées, puis quota — et seulement ensuite l'appel au modèle. Chaque contrôle est placé avant celui qui coûte plus cher. Vérifier le quota après l'inférence aurait permis de consommer le moteur sans jamais être compté.
La journalisation intervient après la réponse du modèle, et elle enregistre le contenu avant et après.
Le cas d'erreur est traité : si Ollama ne répond pas, la couche ia_service traduit l'exception réseau en un message lisible, et aucune ligne n'est écrite dans le journal — sinon un échec consommerait du quota.
Et la décision finale reste à l'utilisateur : rien n'est appliqué au document automatiquement. C'est à la fois une exigence d'ergonomie et une mesure de sécurité — ne jamais appliquer automatiquement la sortie d'un modèle.`);
  s.addText("Cinq contrôles avant le moindre appel au modèle", { placeholder: "title" });
  media(s, { file: `${R}/docs/dossier/fig/seq-uc10.png`, ratio: 1.59, y: 1.45, maxH: 4.9, name: "diagramme de sequence" });
  s.addText("Séquence — génération d'une assistance IA (dossier § 5.7).", { placeholder: "caption" });
}

// ═══════════════════════════ 5. Réalisation ═══════════════════════════

pres.addSection({ title: "Réalisation" });

{
  const s = add("SECTION", "Réalisation",
`[21:30 — 21:40]
« Quatrième temps : la réalisation, avec les écrans et le code. »`);
  s.addText("4", { placeholder: "num" });
  s.addText("La réalisation", { placeholder: "title" });
  s.addText("Dossier § 6 — spécifications techniques  ·  § 7 — écrans et extraits de code", { placeholder: "sub" });
}

{
  const s = add("SPLIT", "Réalisation",
`[21:40 — 22:40]
Le tableau de bord, capture réelle de l'application en fonctionnement.
Trois compteurs en haut, puis trois portes d'entrée vers la rédaction. Ce choix répond à un constat d'usage : devant un éditeur vide, l'utilisateur qui n'a pas de structure en tête abandonne. Proposer un modèle ou un document existant supprime la page blanche.
Techniquement, deux choses. Les compteurs viennent de l'API, pas d'un calcul côté client. Et la recherche filtre la page courante côté client, parce que la pagination est serveur : la liste n'est jamais chargée entièrement.
Huit captures figurent en annexe § 12.2, avec le code correspondant.`);
  s.addText("Supprimer la page blanche", { placeholder: "title" });
  s.addText([
    ...li([
      "Trois compteurs — documents créés, brouillons, finalisés — servis par l'API, jamais recalculés côté client.",
      "Trois portes d'entrée : page blanche, modèle, document existant. Devant un éditeur vide, l'utilisateur sans structure en tête abandonne.",
      "Pagination serveur : la liste n'est jamais chargée entièrement ; la recherche filtre la page courante.",
      "État vide explicite plutôt qu'une zone muette.",
      "Huit captures figurent en annexe § 12.2, avec le code qui les produit.",
    ]),
  ], { placeholder: "body" });
  s.addImage({ path: `${R}/docs/captures/C-05-tableau-de-bord.png`, x: 7.52, y: 1.5, w: 4.66, h: 4.9, shadow: shadow({ blur: 14, offset: 3, opacity: 0.18 }), objectName: "capture C-05" });
  s.addText("Capture C-05 — tableau de bord.", { placeholder: "caption" });
}

{
  const s = add("SPLIT", "Réalisation",
`[22:40 — 24:40]
L'éditeur, l'écran central du produit.
Je m'arrête sur l'enregistrement automatique, parce que quatre décisions tiennent dans quelques lignes.
Le délai de 2,5 secondes n'est pas arbitraire : enregistrer à chaque caractère saturerait l'API et multiplierait les écritures ; un délai trop long rendrait la sauvegarde invisible et ferait perdre du travail.
Le minuteur précédent est systématiquement annulé — sans ça, une frappe rapide empilerait les requêtes.
L'enregistrement différé est doublé d'un bouton explicite : l'utilisateur doit pouvoir forcer la sauvegarde.
Et rien n'est enregistré tant que le titre est vide.
Une remarque de méthode, que j'ai tenu à écrire dans le dossier : sur la capture C-07, l'indicateur d'enregistrement n'apparaît pas, parce qu'aucune frappe n'a eu lieu. En conclure que la fonctionnalité est absente serait une erreur. Une capture atteste d'un état, pas d'un comportement — vérifier une fonctionnalité demande de lire le code ou d'exécuter un scénario. C'est exactement la raison d'être du jeu d'essai.`);
  s.addText("Enregistrer 2,5 s après la dernière frappe", { placeholder: "title" });
  s.addText([
    ...li([
      "2,5 s : enregistrer à chaque caractère saturerait l'API ; un délai trop long ferait perdre du travail.",
      "Le minuteur précédent est annulé à chaque frappe — sinon les requêtes s'empilent.",
      "Doublé d'un bouton explicite : l'utilisateur garde la main.",
      "Rien n'est enregistré tant que le titre est vide.",
      "Une capture atteste d'un état, pas d'un comportement — d'où le jeu d'essai du § 10.",
    ]),
  ], { placeholder: "body" });
  s.addImage({ path: `${R}/docs/captures/C-07-nouveau-document.png`, x: 7.3, y: 2.1, w: 5.4, h: 4.15, shadow: shadow({ blur: 14, offset: 3, opacity: 0.18 }), objectName: "capture C-07" });
  s.addText("Capture C-07 — éditeur, création d'un document.", { placeholder: "caption" });
}

{
  const s = add("CONTENT", "Réalisation",
`[24:40 — 26:40]
Un composant métier : le quota IA. Dix lignes, et trois décisions.
Première décision : c'est une agrégation. Je compte les lignes du journal des appels sur les vingt-quatre dernières heures. Je ne lis pas un compteur stocké sur l'utilisateur. Un compteur se désynchronise — il suffit d'un échec entre l'appel et l'incrément ; une agrégation est toujours juste par construction.
Deuxième décision : c'est une fenêtre glissante, pas un compteur journalier. Le cahier des charges dit « 20 requêtes par 24 heures », pas « par jour calendaire ». Avec un compteur remis à zéro à minuit, un utilisateur fait quarante appels entre 23 h et 1 h.
Troisième décision : le code de retour est 429, Too Many Requests, pas 403. Un 403 dit « vous n'avez pas le droit » ; un 429 dit « réessayez plus tard ». Ce n'est pas la même information pour le client.
Et le contrôle est entièrement côté serveur. Le front affiche le quota restant, mais c'est de l'affichage.
Le test correspondant est le cas JE-07 du jeu d'essai, et mes données de test contiennent une ligne datée de 25 heures précisément pour vérifier la fenêtre glissante.`);
  s.addText("Compter les appels, jamais les stocker", { placeholder: "title" });
  s.addText("Composant métier — le quota IA, contrôlé côté serveur avant tout appel au modèle (dossier § 7.2).", { placeholder: "lead" });

  code(s, { x: M, y: 1.95, w: 7.3, h: 3.9, file: "app/routes/ia_route.py", lines: [
    "window_start = utc_now_naive() - timedelta(hours=24)",
    "",
    "calls_last_24h = db_session.execute(",
    "    select(func.count()).select_from(IA).where(",
    "        IA.user_id    == request.user_id,",
    "        IA.created_at >= window_start,",
    "    )",
    ").scalar_one()",
    "",
    "if calls_last_24h >= current_user.quota_daily_limit:",
    "    return jsonify({\"error\": \"Quota IA atteint.\"}), 429",
  ] });

  const pts = [
    ["Une agrégation, pas un compteur", "Un compteur stocké se désynchronise ; une agrégation est juste par construction."],
    ["Une fenêtre glissante", "« 20 par 24 h », pas « par jour » : sinon 40 appels entre 23 h et 1 h."],
    ["429, pas 403", "« Réessayez plus tard », et non « vous n'avez pas le\u00A0droit\u00A0»."],
  ];
  pts.forEach((p, i) => {
    const y = 1.95 + i * 1.32;
    s.addText(p[0], { x: 8.2, y, w: 4.5, h: 0.36, fontSize: 15, bold: true, color: THEME.colors.accent1, margin: 0, isTextBox: true });
    s.addText(p[1], { x: 8.2, y: y + 0.38, w: 4.5, h: 0.85, fontSize: 14, color: C.text1, margin: 0, isTextBox: true });
  });
  s.addText("Le front affiche le quota restant — mais le contrôle qui compte est celui du serveur.",
    { x: M, y: 6.0, w: CW, h: 0.4, fontSize: 13.5, color: THEME.colors.accent5, margin: 0, isTextBox: true, objectName: "note quota" });
}

{
  const s = add("CONTENT", "Réalisation",
`[26:40 — 27:40]
Un composant d'accès aux données, et c'est le motif le plus répété du projet.
La propriété est dans la clause WHERE. Je ne charge pas le document puis ne compare son propriétaire : je demande à la base un document qui a cet identifiant ET qui appartient à l'utilisateur courant.
La différence n'est pas stylistique. Avec un contrôle a posteriori, il suffit d'oublier un if dans une route pour ouvrir une faille. Ici, oublier la condition fait échouer le test de propriété, qui existe pour chaque ressource.
Conséquence voulue : un identifiant qui appartient à quelqu'un d'autre renvoie 404, pas 403. Un 403 confirmerait que la ressource existe. Le 404 est indiscernable d'un identifiant inexistant.
Et toutes les requêtes passent par l'ORM, paramétrées, sans aucune concaténation de chaîne. C'est l'objectif de qualité que je m'étais fixé et il est tenu sans exception.`);
  s.addText("La propriété est dans le WHERE", { placeholder: "title" });
  s.addText("Composant d'accès aux données — le motif répété pour chaque ressource (dossier § 7.3).", { placeholder: "lead" });

  code(s, { x: M, y: 1.95, w: 7.3, h: 3.4, file: "app/routes/document_route.py", lines: [
    "stmt = select(Document).where(",
    "    Document.id_document == id_document,",
    "    Document.user_id     == request.user_id,",
    ")",
    "document = db_session.execute(stmt).scalar_one_or_none()",
    "",
    "if document is None:",
    "    return jsonify({\"error\": \"Document introuvable\"}), 404",
  ] });

  const pts = [
    ["Filtrer, pas vérifier après", "Oublier la condition fait échouer un test ; oublier un if ouvre une faille."],
    ["404, jamais 403", "Un 403 confirmerait que la ressource existe. Le 404 est indiscernable."],
    ["ORM paramétré, sans exception", "Aucune requête construite par concaténation dans tout le projet."],
  ];
  pts.forEach((p, i) => {
    const y = 1.95 + i * 1.15;
    s.addText(p[0], { x: 8.2, y, w: 4.5, h: 0.36, fontSize: 15, bold: true, color: THEME.colors.accent1, margin: 0, isTextBox: true });
    s.addText(p[1], { x: 8.2, y: y + 0.38, w: 4.5, h: 0.7, fontSize: 14, color: C.text1, margin: 0, isTextBox: true });
  });
  s.addText("Les identifiants étant des UUID v4, ils ne sont de toute façon pas énumérables — défense en profondeur.",
    { x: M, y: 5.55, w: CW, h: 0.4, fontSize: 13.5, color: THEME.colors.accent5, margin: 0, isTextBox: true, objectName: "note uuid" });
}

// ═══════════════════════════ 6. Sécurité ═══════════════════════════

pres.addSection({ title: "Sécurité" });

{
  const s = add("SECTION", "Sécurité",
`[27:40 — 27:50]
« Cinquième temps : la sécurité. C'est le fil rouge du projet, pas un chapitre. »`);
  s.addText("5", { placeholder: "num" });
  s.addText("La sécurité", { placeholder: "title" });
  s.addText("Dossier § 8 — OWASP Top 10, sessions, contrôle d'accès, validation", { placeholder: "sub" });
}

{
  const s = add("CONTENT", "Sécurité",
`[27:50 — 29:50]
Ma grille de lecture est l'OWASP Top 10 2021, croisée avec les exigences du cahier des charges et les recommandations de l'ANSSI. Le dossier traite les dix catégories ; j'en montre six.
Le point de méthode d'abord : la sécurité n'a pas été traitée en fin de projet, et pas par vertu — par nécessité pratique. Le filtrage par propriétaire dans le WHERE, le stockage d'empreintes, le refus de démarrer sans clé : ce sont des choix de structure. Les ajouter après coup aurait demandé de réécrire les couches concernées.
A01, je viens de le montrer : la propriété est dans le WHERE, et le rôle est relu en base, pas lu dans le jeton.
A02 : bcrypt avec sel pour les mots de passe, SHA-256 pour les jetons. Aucun secret en clair en base — une fuite de la base ne permet pas de rejouer une session.
A05 : l'application refuse de démarrer sans JWT_SECRET_KEY. Pas de valeur par défaut, pas de repli silencieux. Une clé de secours en dur est une clé en production.
A10 : la seule URL sortante du projet est OLLAMA_URL, une valeur de configuration. Aucune entrée utilisateur ne devient jamais une destination HTTP.
Je suis transparente sur une faiblesse, elle est dans le dossier : A09, la journalisation applicative est incomplète. Le journal des interactions IA existe, mais il n'y a pas de journalisation systématique des événements de sécurité.`);
  s.addText("La sécurité comme contrainte de conception", { placeholder: "title" });
  s.addText("Grille OWASP Top 10 (2021), croisée avec le cahier des charges et les recommandations de l'ANSSI.", { placeholder: "lead" });

  const owasp = [
    ["A01", "Contrôle d'accès", "Propriété dans le WHERE, rôle relu en base à chaque appel /admin, garde de blueprint."],
    ["A02", "Cryptographie", "bcrypt salé pour les mots de passe, SHA-256 pour les jetons. Aucun secret en clair en base."],
    ["A03", "Injection", "ORM paramétré sans exception ; rendu Markdown assaini par DOMPurify."],
    ["A05", "Configuration", "Sans JWT_SECRET_KEY, l'application refuse de démarrer. CORS restreint à l'origine du front."],
    ["A07", "Identification", "Rotation des refresh tokens, révocation, limitation de débit, politique de mot de passe."],
    ["A10", "SSRF", "Une seule URL sortante : OLLAMA_URL, valeur de configuration, jamais une entrée utilisateur."],
  ];
  owasp.forEach((o, i) => {
    const col = i % 3, row = Math.floor(i / 3);
    card(s, {
      x: M + col * 4.11, y: 2.0 + row * 2.2, w: col === 2 ? 3.88 : 3.87, h: 2.0,
      badge: o[0], title: o[1], body: o[2],
    });
  });
  s.addText("A09 — la journalisation applicative reste incomplète : le journal IA existe, pas la journalisation systématique des événements de sécurité.",
    { x: M, y: 6.45, w: CW, h: 0.4, fontSize: 13, color: THEME.colors.accent4, margin: 0, isTextBox: true, objectName: "faiblesse a09" });
}

{
  const s = add("CONTENT", "Sécurité",
`[29:50 — 32:20]
Le cycle de vie des sessions, parce que c'est la partie du projet qui m'a demandé le plus de réflexion.
Deux besoins contradictoires. Un jeton court est sûr mais oblige à se reconnecter sans arrêt. Un jeton long est confortable mais dangereux. La combinaison des deux donne les deux propriétés : un access token de quinze minutes, non révocable mais à fenêtre d'exposition courte ; un refresh token de sept jours, révocable côté serveur.
Le refresh token vit dans un cookie httpOnly, SameSite Strict, limité au chemin /auth. Inaccessible au JavaScript : même une faille XSS ne permet pas de le lire.
Et ce que je stocke en base n'est pas le jeton, c'est son empreinte SHA-256. Une fuite de la base ne permet pas de rejouer une session.
Le code à droite est le cœur du mécanisme. À chaque usage, le jeton présenté est marqué consommé et un nouveau est émis. Si un jeton déjà consommé se représente, il n'y a que deux explications : soit l'utilisateur rejoue une vieille requête, soit quelqu'un a volé le jeton. Dans le doute, je révoque toutes les sessions du compte. C'est volontairement brutal — la gêne est un reconnexion, le risque évité est un compte compromis.
Dernier point, et c'est celui qu'on oublie le plus souvent : à la réinitialisation du mot de passe, toutes les sessions sont supprimées. Changer son mot de passe après une compromission ne sert à rien si les sessions ouvertes par l'attaquant survivent.
Une précision sur la purge : la tâche purge_expired_sessions filtre sur l'expiration du jeton, pas sur le drapeau revoke. Une session révoquée doit survivre jusqu'au terme de son jeton — sinon un jeton volé puis rejoué ne serait plus reconnu comme un rejeu, et la détection de vol tomberait.`);
  s.addText("Un jeton court non révocable, un jeton long révocable", { placeholder: "title" });
  s.addText("Deux besoins contradictoires, résolus par deux jetons de nature différente (dossier § 8).", { placeholder: "lead" });

  const el = [
    ["Access token", "JWT HS256, 15 minutes, en-tête Authorization, jamais stocké en base."],
    ["Refresh token", "64 octets aléatoires, cookie httpOnly / Secure / SameSite=Strict / path=/auth, 7 jours."],
    ["Stockage", "Empreinte SHA-256 uniquement : une fuite de la base ne permet pas de rejouer une session."],
  ];
  el.forEach((e, i) => {
    const y = 1.95 + i * 1.6;
    s.addShape(pres.ShapeType.roundRect, { x: M, y, w: 6.1, h: 1.3, rectRadius: 0.06, fill: { color: C.background2 }, line: { color: C.background2 }, shadow: shadow(), objectName: `session ${e[0]}` });
    s.addText(e[0], { x: M + 0.28, y: y + 0.18, w: 5.5, h: 0.34, fontSize: 16, bold: true, color: THEME.colors.accent1, margin: 0, isTextBox: true });
    s.addText(e[1], { x: M + 0.28, y: y + 0.56, w: 5.54, h: 0.6, fontSize: 14.5, color: C.text1, valign: "top", margin: 0, isTextBox: true });
  });

  code(s, { x: 7.0, y: 1.95, w: 5.7, h: 3.0, file: "app/services/auth_service.py", size: 11, lines: [
    "if session.revoke:",
    "    revoke_all_user_sessions(",
    "        session.user_id, db_session)",
    "    db_session.commit()",
    "    raise ValueError(",
    "        \"Réutilisation détectée\")",
    "",
    "session.revoke = True",
  ] });
  s.addText("Rejouer un jeton déjà consommé est traité comme un vol : toutes les sessions du compte sont révoquées. La gêne est une reconnexion ; le risque évité est un compte compromis.\n\nÀ la réinitialisation du mot de passe, toutes les sessions sont également supprimées : changer son mot de passe ne sert à rien si les sessions de l'attaquant survivent.",
    { x: 7.0, y: 5.1, w: 5.7, h: 1.75, fontSize: 14, color: C.text1, valign: "top", margin: 0, isTextBox: true, objectName: "note rotation" });
}

// ═══════════════════════════ 7. Tests, veille, bilan ═══════════════════════════

pres.addSection({ title: "Tests, veille et bilan" });

{
  const s = add("SECTION", "Tests, veille et bilan",
`[32:20 — 32:30]
« Dernier temps : comment je vérifie, comment je me tiens à jour, et ce que je retiens. »`);
  s.addText("6", { placeholder: "num" });
  s.addText("Tests, veille et bilan", { placeholder: "title" });
  s.addText("Dossier § 9 — plan de tests  ·  § 10 — jeu d'essai  ·  § 11 — veille", { placeholder: "sub" });
}

{
  const s = add("CONTENT", "Tests, veille et bilan",
`[32:30 — 34:30]
Le plan de tests est organisé en quatre niveaux, du moins coûteux au plus coûteux. Ce classement détermine ce qui tourne à chaque push et ce qui reste manuel.
Les chiffres de la campagne du 3 octobre : 195 cas, tous au vert, en 59 secondes. 95 % de couverture backend — 100 % sur services/ et sur la couche de persistance, 89 à 96 % sur les routes.
Mon objectif de couverture était 80 % sur services/ et sur les routes, sans objectif chiffré ailleurs. C'est volontaire : viser un pourcentage global pousse à écrire des tests faciles sur du code sans risque. Les 62 % du front sont tirés vers le bas par cinq modules de service qui sont des enveloppes d'une ligne autour d'axios — les tester reviendrait à tester axios.
Trois zones concentrent l'effort : la chaîne d'authentification, le contrôle de propriété, et le quota. Ce sont les trois endroits où une régression coûte cher.
Et la leçon que je retiens de la campagne : les doubles de test mentent. Trois défauts de la chaîne IA sont passés sous un faux requests.post qui acceptait json() à tout moment et ne fermait jamais de connexion. Il a fallu un vrai serveur HTTP local pour les voir. Les tests ajoutés ensuite ont été vérifiés par mutation : on casse le code exprès pour s'assurer que le test échoue. Un test qu'on n'a jamais vu échouer ne prouve rien.
Ce qui reste : les tests système attendent une machine avec un démon Docker, et les tests de charge viennent après.`);
  s.addText("195 cas au vert, 95 % de couverture backend", { placeholder: "title" });
  s.addText("Campagne du 3 octobre 2026 — quatre niveaux, du moins coûteux au plus coûteux à exécuter.", { placeholder: "lead" });

  stat(s, { x: M, y: 1.9, w: 2.9, h: 1.3, value: "195", label: "cas automatisés, tous au vert" });
  stat(s, { x: M + 3.07, y: 1.9, w: 2.9, h: 1.3, value: "95 %", label: "couverture backend" });
  stat(s, { x: M + 6.14, y: 1.9, w: 2.9, h: 1.3, value: "59 s", label: "durée de la campagne" });
  stat(s, { x: M + 9.21, y: 1.9, w: 2.89, h: 1.3, value: "100 %", label: "sur services/ et la persistance" });

  const niv = [
    ["Analyse statique", "vue-tsc, Ruff", "à chaque push"],
    ["Tests unitaires", "pytest, Vitest", "à chaque push"],
    ["Tests d'intégration", "pytest + client Flask", "à chaque push"],
    ["Tests fonctionnels", "cahier de tests manuel", "fin d'itération"],
  ];
  niv.forEach((v, i) => {
    const x = M + i * 3.07;
    s.addShape(pres.ShapeType.roundRect, { x, y: 3.45, w: i === 3 ? 2.89 : 2.9, h: 1.55, rectRadius: 0.06, fill: { color: C.background2 }, line: { color: C.background2 }, shadow: shadow(), objectName: `niveau ${v[0]}` });
    s.addText(v[0], { x: x + 0.22, y: 3.62, w: 2.46, h: 0.5, fontSize: 15, bold: true, color: C.text1, margin: 0, isTextBox: true });
    s.addText(v[1], { x: x + 0.22, y: 4.14, w: 2.46, h: 0.34, fontSize: 13, color: THEME.colors.accent5, margin: 0, isTextBox: true });
    s.addText(v[2], { x: x + 0.22, y: 4.5, w: 2.46, h: 0.34, fontSize: 13, bold: true, color: THEME.colors.accent3, margin: 0, isTextBox: true });
  });

  card(s, { x: M, y: 5.2, w: CW, h: 1.42, badge: "!", accent: THEME.colors.accent4, title: "Les doubles de test mentent",
    body: "Trois défauts sont passés sous un faux requests.post trop permissif. Il a fallu un vrai serveur HTTP pour les voir. Les tests ajoutés ensuite ont été vérifiés par mutation — un test qu'on n'a jamais vu échouer ne prouve rien." });
}

{
  const s = add("CONTENT", "Tests, veille et bilan",
`[34:30 — 36:30]
Le jeu d'essai porte sur la génération d'une assistance IA. Je l'ai choisi pour trois raisons : il traverse les trois couches et sollicite un système externe, il concentre cinq contrôles de nature différente, et il porte les deux exigences les plus délicates du cahier des charges — le quota et la traçabilité.
C'est aussi la seule fonctionnalité qu'aucune capture d'écran ne peut attester, puisqu'elle se manifeste par un enchaînement et non par un état.
Les données sont construites par un script, pour être reproductibles à l'identique. Quatre comptes : l'utilisatrice principale, un tiers pour les accès croisés, un administrateur, et un compte au quota abaissé à 1 pour atteindre la limite en un seul appel.
La donnée la plus utile du jeu est celle de droite : dans le journal du compte U1, dix-neuf lignes datées de moins de vingt-quatre heures, et une ligne datée de vingt-cinq heures.
Cette ligne unique est le seul moyen de distinguer une fenêtre glissante d'un compteur journalier. Sans elle, le cas JE-07 passerait quelle que soit l'implémentation.
C'est ce que j'ai appris en construisant ce jeu : un jeu de données, ce n'est pas remplir des tables — c'est choisir les valeurs qui font échouer les mauvaises implémentations.`);
  s.addText("La ligne datée de 25 heures", { placeholder: "title" });
  s.addText("Jeu d'essai sur POST /documents/<id>/ia/generer — la fonctionnalité la plus significative du projet.", { placeholder: "lead" });

  card(s, { x: M, y: 1.95, w: 3.87, h: 2.4, badge: "?", title: "Pourquoi cette route",
    body: "Elle traverse les trois couches et un système externe, concentre cinq contrôles, et porte les deux exigences les plus délicates : quota et traçabilité." });
  card(s, { x: M + 4.11, y: 1.95, w: 3.87, h: 2.4, badge: "4", title: "Quatre comptes",
    body: "U1 utilisatrice principale · U2 tiers, pour l'accès croisé · U3 administrateur · U4 quota abaissé à 1, pour atteindre la limite en un appel." });
  card(s, { x: M + 8.22, y: 1.95, w: 3.88, h: 2.4, badge: "25 h", accent: THEME.colors.accent3, title: "La donnée décisive",
    body: "19 lignes de moins de 24 h, et 1 ligne datée de 25 h. Seule façon de distinguer une fenêtre glissante d'un compteur journalier." });

  s.addText([
    { text: "Ce que j'en retiens.  ", options: { bold: true } },
    { text: "Construire un jeu de données, ce n'est pas remplir des tables : c'est choisir les valeurs qui font échouer les mauvaises implémentations. Sans la ligne à 25 heures, le cas JE-07 passerait quelle que soit l'implémentation du quota.", options: {} },
  ], { x: M, y: 4.7, w: CW, h: 1.0, fontSize: 15, color: THEME.colors.dk1, margin: 0, isTextBox: true, objectName: "lecon jeu d'essai" });

  s.addText("Les adresses utilisent le domaine réservé .test et les mots de passe sont des valeurs de test : aucune donnée personnelle réelle dans le jeu d'essai.",
    { x: M, y: 5.85, w: CW, h: 0.4, fontSize: 13, color: THEME.colors.accent5, margin: 0, isTextBox: true, objectName: "note rgpd jeu" });
}

{
  const s = add("CONTENT", "Tests, veille et bilan",
`[36:30 — 38:30]
Ma veille porte sur trois périmètres : les dépendances, la sécurité applicative, le réglementaire. Le principe est de surveiller ce que le projet utilise réellement — une alerte sur une bibliothèque absente du projet n'est pas une information.
Huit entrées sur six mois, trois ont appelé une action. C'est la mesure de l'utilité de l'exercice.
Le premier constat est dans le titre : la sévérité publiée ne prédit pas l'impact réel. La CVE la plus sévère de ma liste, 9,1 sur Ollama, était atténuée par ma configuration — le serveur n'écoutait que sur localhost. La plus modérée, 5,1 sur DOMPurify, affectait directement ma version.
DOMPurify est l'entrée la plus instructive, parce que c'est la bibliothèque que j'avais ajoutée précisément pour corriger une faille XSS. Découvrir qu'elle porte elle-même une vulnérabilité de contournement établit un principe : une mesure de sécurité est un composant comme un autre, avec sa propre surface d'attaque. Ajouter une bibliothèque d'assainissement ne clôt pas le sujet XSS, elle le déplace vers la maintenance de cette bibliothèque. D'où la valeur de la défense en profondeur : je stocke du Markdown brut, pas du HTML — si DOMPurify échoue, la donnée stockée n'est toujours pas exécutable.
Ollama éclaire rétrospectivement mon choix d'architecture : héberger soi-même, c'est aussi maintenir soi-même. La décision reste la bonne au regard du RGPD, mais elle se paie en maintenance, et le dire est plus honnête que de la présenter comme un choix sans contrepartie.
Et l'AI Act justifie à lui seul la veille comme livrable : le cahier des charges, rédigé avant l'entrée en application, ne mentionne que le RGPD. Sans ce suivi, j'aurais livré une application non conforme à une obligation entrée en vigueur trois semaines avant la fin du développement.`);
  s.addText("La sévérité publiée ne prédit pas l'impact réel", { placeholder: "title" });
  s.addText("Huit entrées entre avril et septembre 2026, trois ont appelé une action. Journal complet : docs/veille-helpmedraft.html", { placeholder: "lead" });

  card(s, { x: M, y: 1.95, w: 3.87, h: 2.9, badge: "5.1", accent: THEME.colors.accent3, title: "DOMPurify — corrigé",
    body: "CVE-2026-0540, contournement du nettoyage XSS. Version affectée : la mienne. Mise à jour en 3.4.16 le 02/10/2026.\n\nUne mesure de sécurité est un composant comme un autre." });
  card(s, { x: M + 4.11, y: 1.95, w: 3.87, h: 2.9, badge: "9.1", accent: THEME.colors.accent3, title: "Ollama — corrigé",
    body: "CVE-2026-7482, lecture hors limites sans authentification. Atténuée par l'écoute sur localhost seule. Mise à jour en 0.35.1.\n\nHéberger soi-même, c'est maintenir soi-même." });
  card(s, { x: M + 8.22, y: 1.95, w: 3.88, h: 2.9, badge: "UE", accent: THEME.colors.accent4, title: "AI Act — en cours",
    body: "Transparence applicable depuis le 02/08/2026. Partiellement couvert ; trois compléments identifiés : mention au premier usage, marquage des passages générés, clause CGU." });

  s.addText([
    { text: "axios, 31 mars 2026 — ", options: { bold: true } },
    { text: "deux versions piégées publiées après la compromission d'un compte mainteneur npm. Projet non affecté. Pas de CVE : ce n'est pas un défaut de code, c'est le canal de distribution qui a été attaqué. C'est le fichier package-lock.json, commité, qui permet de le prouver après coup.", options: {} },
  ], { x: M, y: 5.2, w: CW, h: 1.1, fontSize: 14.5, color: THEME.colors.dk1, margin: 0, isTextBox: true, objectName: "axios" });
}

{
  const s = add("CLOSE", "Tests, veille et bilan",
`[38:30 — 40:00]
Pour conclure, trois colonnes.
Ce qui est livré : l'application complète sur les cinq lots fonctionnels, 195 tests au vert, la conteneurisation et le pipeline, les audits d'accessibilité et de sécurité, et le journal de veille.
Ce qui reste, et je ne le cache pas : le déploiement effectif, la bascule complète vers MySQL — le schéma est exécuté et vérifié, il me manque une machine avec un démon Docker —, les trois compléments AI Act, et une journalisation applicative à compléter.
Ce que je retiens, ce sont trois phrases que ce projet m'a apprises et pas un cours.
Un prompt est du code : il part en production, il oriente le comportement, et il se teste.
Une mesure de sécurité est un composant comme un autre : ajouter DOMPurify n'a pas clos le sujet XSS, ça l'a déplacé vers sa maintenance.
Et un jeu de données, c'est le choix des valeurs qui font échouer les mauvaises implémentations.
Je vous remercie, je suis à votre disposition pour vos questions.`);
  s.addText("Ce que je retiens", { placeholder: "title" });

  const cols = [
    ["Livré", THEME.colors.accent3, "Cinq lots fonctionnels complets\n195 tests automatisés au vert\nDocker Compose et pipeline CI\nAudits accessibilité et sécurité\nJournal de veille et dossier projet"],
    ["Reste à faire", THEME.colors.accent1, "Déploiement effectif\nBascule complète SQLite → MySQL\nTrois compléments AI Act\nJournalisation applicative\nTests système et de charge"],
    ["Appris", "E6EBF5", "Un prompt est du code : il se teste\nUne mesure de sécurité est un composant comme un autre\nUn jeu de données, c'est choisir les valeurs qui font échouer"],
  ];
  cols.forEach((c, i) => {
    const x = M + i * 4.11;
    const w = i === 2 ? 3.88 : 3.87;
    s.addShape(pres.ShapeType.roundRect, { x, y: 1.85, w, h: 3.05, rectRadius: 0.08, fill: { color: "1E2740" }, line: { color: "1E2740" }, objectName: `bilan ${c[0]}` });
    s.addText(c[0], { x: x + 0.3, y: 2.1, w: w - 0.6, h: 0.45, fontSize: 19, bold: true, color: c[1], margin: 0, isTextBox: true });
    s.addText(c[2], { x: x + 0.3, y: 2.62, w: w - 0.6, h: 2.55, fontSize: 14.5, color: "E6EBF5", lineSpacing: 23, valign: "top", margin: 0, isTextBox: true });
  });

  s.addText("Merci de votre attention.", { x: M, y: 5.35, w: CW, h: 0.6, fontSize: 24, bold: true, color: THEME.colors.accent1, margin: 0, isTextBox: true, objectName: "merci" });
}

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log(`écrit : ${OUT} — ${n} diapositives`);
})();
