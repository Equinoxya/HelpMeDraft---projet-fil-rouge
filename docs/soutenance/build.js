// Support de soutenance CDA — HelpMeDraft
// Contenu repris du dossier projet (docs/Dossier-projet-HelpMeDraft.pdf) pour
// qu'aucune affirmation du diaporama ne contredise ce que le jury a lu.

const pptxgen = require("pptxgenjs");
const { applyTheme } = require("/root/.claude/skills/synced/c1c8c12f-8277-41a7-a992-cea745916b4e_fa19c528-ebca-4d79-893f-2c00c15e48d4/pptx/scripts/apply_theme.js");

const R = "/home/user/HelpMeDraft---projet-fil-rouge";
const OUT = process.argv[2] || "Soutenance-HelpMeDraft.pptx";

// La charte est celle de l'application : parchemin, noir plein, accent brique.
// #C4341C est la teinte retenue APRÈS l'audit d'accessibilité du 03/10 (l'accent
// d'origine #E0533C ne tenait pas le 4,5:1 sur fond clair) ; il reste utilisé sur
// les fonds noirs, où c'est lui qui passe le seuil.
const THEME = {
  name: "HelpMeDraft",
  headFontFace: "Georgia",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "111111", // texte et bordures
    lt1: "F4F1EA", // fond parchemin
    dk2: "111111", // fond des diapositives sombres
    lt2: "FAF8F5", // surface des cartes
    accent1: "C4341C", // accent brique, sur fond clair
    accent2: "A72C18", // survol
    accent3: "1F6F4A", // vert — acquis
    accent4: "C4341C", // risque : même brique, la charte n'a qu'un rouge
    accent5: "5A554C", // gris chaud sur fond clair
    accent6: "A8A194", // gris chaud sur fond noir
    hlink: "C4341C",
    folHlink: "5A554C",
  },
};
const ACCENT_SOMBRE = "E0533C"; // accent éclairci, lisible sur #111111

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.3 x 7.5
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.author = "Ophélie Bellissens";
pres.title = "HelpMeDraft — soutenance CDA";
pres.subject = "Dossier projet CDA — HelpMeDraft";

const C = pres.SchemeColor;
const W = 13.3, H = 7.5, M = 0.6, CW = W - 2 * M; // 12.1

const FOOT = "HelpMeDraft  ·  Ophélie Bellissens  ·  CDA — Metz Numeric School";
// 8px 8px 0 #111111 : la charte pose une ombre sans flou. Un effet d'ombre est
// rendu différemment selon le lecteur ; un rectangle noir décalé derrière le bloc
// donne exactement le même aplat partout.
const BORD = { color: "111111", width: 1.25 };
const DEC = 0.07; // décalage de l'ombre, en pouces
function bloc(s, { x, y, w, h, fill, line, name }) {
  s.addShape(pres.ShapeType.rect, {
    x: x + DEC, y: y + DEC, w, h,
    fill: { color: "111111" }, line: { color: "111111", width: 0.75 },
    objectName: `ombre ${name}`,
  });
  s.addShape(pres.ShapeType.rect, {
    x, y, w, h, fill: { color: fill }, line: line || { ...BORD }, objectName: name,
  });
}

// ───────────────────────────── layouts ─────────────────────────────

const footLight = [
  { text: { text: FOOT, options: { x: M, y: 6.98, w: 8, h: 0.3, fontSize: 9, color: THEME.colors.accent5, fontFace: "Courier New", isTextBox: true, objectName: "pied" } } },
];
const footDark = [
  { text: { text: FOOT, options: { x: M, y: 6.98, w: 8, h: 0.3, fontSize: 9, color: THEME.colors.accent6, fontFace: "Courier New", isTextBox: true, objectName: "pied" } } },
];
const numLight = { x: 12.5, y: 6.98, w: 0.4, h: 0.3, fontSize: 9, color: THEME.colors.accent5, align: "right" };
const numDark = { x: 12.5, y: 6.98, w: 0.4, h: 0.3, fontSize: 9, color: THEME.colors.accent6, align: "right" };

pres.defineSlideMaster({
  title: "TITLE",
  background: { color: C.text2 },
  objects: [
    { placeholder: { options: { name: "kicker", type: "body", x: M + 0.3, y: 1.9, w: CW, h: 0.4, fontSize: 13, color: ACCENT_SOMBRE, bold: true, charSpacing: 3, fontFace: "Courier New" }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", align: "left", x: M + 0.3, y: 2.4, w: 11.6, h: 1.5, fontSize: 40, bold: true, color: C.background1, valign: "top" }, text: "" } },
    { placeholder: { options: { name: "subtitle", type: "body", x: M + 0.3, y: 3.95, w: 11.0, h: 0.9, fontSize: 19, color: C.background2 }, text: "" } },
    { placeholder: { options: { name: "meta", type: "body", x: M + 0.3, y: 5.5, w: 11.0, h: 1.0, fontSize: 14, color: C.accent6 }, text: "" } },
  ],
});

pres.defineSlideMaster({
  title: "SECTION",
  background: { color: C.text2 },
  objects: [
    { placeholder: { options: { name: "num", type: "body", x: M + 0.3, y: 2.0, w: 2.2, h: 1.6, fontSize: 80, bold: true, color: ACCENT_SOMBRE, valign: "bottom" }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", align: "left", x: M + 0.3, y: 3.7, w: 11.6, h: 1.0, fontSize: 32, bold: true, color: C.background1, valign: "top" }, text: "" } },
    { placeholder: { options: { name: "sub", type: "body", x: M + 0.3, y: 4.7, w: 11.0, h: 0.5, fontSize: 15, color: C.accent6 }, text: "" } },
  ],
  slideNumber: numDark,
});

pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: C.background1 },
  objects: [
    ...footLight,
    { placeholder: { options: { name: "title", type: "title", align: "left", x: M, y: 0.42, w: CW, h: 0.9, fontSize: 26, bold: true, color: C.text1, valign: "bottom" }, text: "" } },
    { placeholder: { options: { name: "lead", type: "body", x: M, y: 1.38, w: CW, h: 0.42, fontSize: 14, color: C.accent5 }, text: "" } },
  ],
  slideNumber: numLight,
});

pres.defineSlideMaster({
  title: "MEDIA",
  background: { color: C.background1 },
  objects: [
    ...footLight,
    { placeholder: { options: { name: "title", type: "title", align: "left", x: M, y: 0.42, w: CW, h: 0.9, fontSize: 26, bold: true, color: C.text1, valign: "bottom" }, text: "" } },
    { placeholder: { options: { name: "caption", type: "body", x: M, y: 6.52, w: CW, h: 0.35, fontSize: 11, color: C.accent5, italic: true }, text: "" } },
  ],
  slideNumber: numLight,
});

pres.defineSlideMaster({
  title: "SPLIT",
  background: { color: C.background1 },
  objects: [
    ...footLight,
    { placeholder: { options: { name: "title", type: "title", align: "left", x: M, y: 0.42, w: CW, h: 0.9, fontSize: 26, bold: true, color: C.text1, valign: "bottom" }, text: "" } },
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
    { placeholder: { options: { name: "title", type: "title", align: "left", x: M, y: 0.6, w: CW, h: 0.9, fontSize: 30, bold: true, color: C.background1, valign: "bottom" }, text: "" } },
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
  bloc(s, { x, y, w, h, fill: C.background2, name: `carte ${title}` });
  let tx = x + 0.3;
  if (badge) {
    const bw = Math.max(0.46, 0.17 + 0.11 * badge.length);
    s.addShape(pres.ShapeType.rect, { x: x + 0.3, y: y + 0.26, w: bw, h: 0.42, fill: { color: col }, line: { ...BORD }, objectName: `pastille ${badge}` });
    s.addText(badge.toUpperCase(), { x: x + 0.3, y: y + 0.26, w: bw, h: 0.42, fontSize: 12, bold: true, color: "F4F1EA", fontFace: "Courier New", align: "center", valign: "middle", margin: 0, isTextBox: true });
    tx = x + 0.3 + bw + 0.22;
  }
  s.addText(title, { x: tx, y: y + 0.24, w: x + w - 0.3 - tx, h: 0.46, fontSize: 15, bold: true, color: C.text1, valign: "middle", margin: 0, isTextBox: true });
  if (body) {
    s.addText(body, { x: x + 0.28, y: y + 0.78, w: w - 0.56, h: h - 1.02, fontSize: 14, color: C.text1, valign: "top", margin: 0, lineSpacing: 19, isTextBox: true });
  }
}

// tuile de chiffre
function stat(s, { x, y, w, h, value, label }) {
  bloc(s, { x, y, w, h, fill: C.background2, name: `chiffre ${value}` });
  s.addText(value, { x: x + 0.2, y: y + 0.12, w: w - 0.4, h: 0.62, fontSize: 34, bold: true, color: C.accent1, align: "center", valign: "middle", margin: 0, isTextBox: true });
  s.addText(label, { x: x + 0.2, y: y + 0.72, w: w - 0.4, h: h - 0.86, fontSize: 13, color: C.text1, align: "center", valign: "top", margin: 0, isTextBox: true });
}

// bloc de code sur fond sombre
function code(s, { x, y, w, h, lines, file, size = 11.5 }) {
  bloc(s, { x, y, w, h, fill: C.text2, name: `code ${file || ""}` });
  if (file) {
    s.addText(file, { x: x + 0.3, y: y + 0.16, w: w - 0.6, h: 0.28, fontSize: 10.5, color: ACCENT_SOMBRE, fontFace: "Courier New", margin: 0, isTextBox: true });
  }
  s.addText(lines.join("\n"), {
    x: x + 0.3, y: y + (file ? 0.5 : 0.24), w: w - 0.6, h: h - (file ? 0.74 : 0.48),
    fontSize: size, fontFace: "Courier New", color: "F4F1EA", lineSpacing: size * 1.5,
    valign: "top", margin: 0, isTextBox: true,
  });
}

// image ajustée dans une zone
function media(s, { file, ratio, x = M, y = 1.5, maxW = CW, maxH = 4.85, name }) {
  let w = Math.min(maxW, maxH * ratio);
  let h = w / ratio;
  const px = x + (maxW - w) / 2;
  const py = y + (maxH - h) / 2;
  bloc(s, { x: px, y: py, w, h, fill: "FFFFFF", name: `cadre ${name || "figure"}` });
  s.addImage({ path: file, x: px, y: py, w, h, objectName: name || "figure" });
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
  s.addText("Six temps. Les numéros renvoient aux sections du dossier.", { placeholder: "lead" });

  // Pas de durée par partie : le minutage est dans les notes de l'orateur,
  // il n'a pas à être affiché au jury — qui le lirait comme un engagement.
  const items = [
    ["1", "Le contexte et le besoin", "Dossier § 2 et § 3"],
    ["2", "La gestion de projet", "§ 4"],
    ["3", "La conception", "§ 5"],
    ["4", "La réalisation", "§ 6 et § 7"],
    ["5", "La sécurité", "§ 8"],
    ["6", "Tests, veille et bilan", "§ 9, § 10, § 11"],
  ];
  items.forEach((it, i) => {
    const y = 1.95 + i * 0.8;
    s.addShape(pres.ShapeType.rect, { x: M + 0.1, y: y + 0.08, w: 0.46, h: 0.46, fill: { color: C.accent1 }, line: { ...BORD }, objectName: `puce ${it[0]}` });
    s.addText(it[0], { x: M + 0.1, y: y + 0.08, w: 0.46, h: 0.46, fontSize: 13, bold: true, color: "F4F1EA", fontFace: "Courier New", align: "center", valign: "middle", margin: 0, isTextBox: true });
    s.addText(it[1], { x: M + 0.85, y: y, w: 7.6, h: 0.62, fontSize: 19, bold: true, color: C.text1, valign: "middle", margin: 0, isTextBox: true });
    s.addText(it[2], { x: 9.1, y: y, w: 3.6, h: 0.62, fontSize: 13, color: C.accent5, fontFace: "Courier New", align: "right", valign: "middle", margin: 0, isTextBox: true });
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
  s.addText("Le constat et la demande", { placeholder: "title" });
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
Le planning reprend celui du cahier des charges. Les six étapes sont engagées et les treize lots fonctionnels sont terminés. La pile conteneurisée a été exécutée pour de vrai : une campagne complète sur un démon Docker réel le 5 octobre, MySQL 8.4 comprise, puis la pile relancée sur mon poste. Restent deux compléments, que j'assume et qui sont écrits dans le dossier : la mention de transparence AI Act, et une journalisation applicative à étoffer.
Sur la gestion de versions : une branche par fonctionnalité, des commits conventionnés, le .env ignoré. Et le package-lock.json commité — ce n'est pas un détail d'organisation, c'est une mesure de sécurité, et la compromission d'axios que je présenterai en fin d'exposé montre pourquoi.
Travaillant seule, j'ai remplacé les rituels d'équipe par un point hebdomadaire avec mon référent et des revues croisées avec la promotion sur la chaîne d'authentification.`);
  s.addText("La méthode et le planning", { placeholder: "title" });

  stat(s, { x: M, y: 1.42, w: 3.9, h: 1.25, value: "1 semaine", label: "durée d'une itération" });
  stat(s, { x: M + 4.1, y: 1.42, w: 3.9, h: 1.25, value: "6 / 6", label: "étapes du plan engagées" });
  stat(s, { x: M + 8.2, y: 1.42, w: 3.9, h: 1.25, value: "13", label: "lots fonctionnels terminés" });

  media(s, { file: `${R}/docs/conception/diagrammes/planning-initial-gantt.png`, ratio: 2.48, y: 2.95, maxH: 3.4, name: "planning initial" });
  s.addText("Planning initial repris du cahier des charges et découpé en lots verticaux.", { placeholder: "caption" });
}

{
  const s = add("CONTENT", "Gestion de projet",
`[6:20 — 8:35]
Trois arbitrages résument le projet.
Le premier : un JWT seul ne se révoque pas. J'ai donc ajouté une table user_session côté serveur et une rotation des refresh tokens. Chaque usage invalide le précédent ; si un jeton déjà consommé revient, c'est qu'il a été volé, et toutes les sessions du compte sont révoquées.
Le deuxième : le quota. Je le calcule par agrégation sur le journal des appels IA, pas avec un compteur stocké sur l'utilisateur. Un compteur peut se désynchroniser ; une agrégation, non. Et l'historique reste auditable, ce qui sert aussi la traçabilité RGPD.
Le troisième est le plus structurant : la confidentialité. Plutôt que d'anonymiser des textes libres — ce qui n'est jamais exhaustif —, j'héberge le modèle en local avec Ollama. L'exigence est satisfaite par construction. Les contreparties sont réelles et je les assume : plus de latence, une qualité inférieure à GPT-4, un prérequis d'installation, et un service de plus à maintenir. Ma veille l'a confirmé : une CVE critique sur Ollama en avril.
Les trois se rejoignent sur un même point, et c'est le fil du projet : chaque exigence du cahier des charges est tenue par la structure du code, et non par une vérification ajoutée après coup.`);
  s.addText("Les arbitrages techniques", { placeholder: "title" });
  s.addText("Les trois décisions qui structurent le projet.", { placeholder: "lead" });

  card(s, { x: M, y: 1.95, w: 3.87, h: 4.5, badge: "1", title: "Session révocable",
    body: "Un JWT est signé, pas enregistré : le serveur le vérifie sans rien stocker. Personne ne peut donc l'annuler avant son échéance — ni moi, ni l'utilisateur qui se croit déconnecté.\n\nD'où la table user_session : chaque session y est inscrite, et révocable.\n\nEt une rotation : chaque usage invalide le précédent. Un jeton rejoué est traité comme un vol — toutes les sessions tombent." });
  card(s, { x: M + 4.11, y: 1.95, w: 3.87, h: 4.5, badge: "2", title: "Quota par agrégation",
    body: "Comptage sur le journal des appels, pas un compteur stocké sur l'utilisateur.\n\nLa valeur ne peut pas se désynchroniser, et l'historique reste auditable — ce qui sert aussi la traçabilité." });
  card(s, { x: M + 8.22, y: 1.95, w: 3.88, h: 4.5, badge: "3", title: "Confidentialité",
    body: "Plutôt qu'anonymiser des textes libres — ce qui n'est jamais exhaustif —, le modèle est hébergé sur place.\n\nLes contenus ne quittent pas l'infrastructure : l'exigence est satisfaite par construction, et non par une clause de contrat." });

  s.addText("Les trois tiennent une exigence du cahier des charges par la structure du code, et non par une vérification ajoutée après coup.",
    { x: M, y: 6.62, w: CW, h: 0.4, fontSize: 13.5, color: THEME.colors.accent5, margin: 0, isTextBox: true, objectName: "fil des arbitrages" });
}

// ═══════════════════════════ 4. Conception ═══════════════════════════

pres.addSection({ title: "Conception" });

{
  const s = add("SECTION", "Conception",
`[8:35 — 8:45]
« Troisième temps, le plus long : la conception. »`);
  s.addText("3", { placeholder: "num" });
  s.addText("La conception", { placeholder: "title" });
  s.addText("Dossier § 5 — architecture, maquettes, modèle de données, cas d'utilisation", { placeholder: "sub" });
}

{
  const s = add("CONTENT", "Conception",
`[8:45 — 9:40]
La pile, domaine par domaine. Je la mets en regard de l'environnement technique recommandé par le cahier des charges, parce que c'est la première question qu'on pose.
Sur sept domaines, six sont conformes. Python et Flask côté serveur, JWT pour l'authentification, GitHub Actions pour l'intégration continue, Docker et docker-compose pour la conteneurisation : c'est ce qui était recommandé, et je n'avais aucune raison de m'en écarter.
Deux lignes sont des choix à l'intérieur d'une alternative que le cahier des charges ouvre lui-même : il dit « MySQL ou MongoDB », et il dit « OpenAI ou un modèle local ». Choisir dans une alternative n'est pas s'écarter d'une recommandation ; c'est trancher, et je justifie les deux à la diapositive suivante.
Il reste un seul véritable écart, le front : le cahier des charges recommande React, j'ai retenu Vue 3. Je l'argumente aussi à la diapositive suivante.
Deux lignes ne figurent pas au cahier des charges et sont des ajouts de ma part. CodeMirror 6, parce qu'un éditeur Markdown avec coloration et raccourcis ne s'écrit pas à la main dans un textarea. Et DOMPurify, parce que la prévisualisation rend du HTML produit à partir du texte de l'utilisateur — c'est le seul v-html du projet, et il est assaini.
Dernière ligne, SQLite : ce n'est pas un second SGBD, c'est le même code SQLAlchemy exécuté sur un moteur de développement. Les tests tournent dessus en mémoire, en quelques secondes et sans serveur.`);
  s.addText("La pile technique", { placeholder: "title" });
  s.addText("Comparée à l'environnement technique recommandé au § 4 du cahier des charges.", { placeholder: "lead" });

  // Trois états : conforme à la recommandation, choix dans une alternative
  // que le cahier des charges ouvre lui-même, écart assumé, ou ajout.
  const VERT = "1F6F4A", BRIQUE = THEME.colors.accent1, GRIS = THEME.colors.accent5;
  const pile = [
    ["Front-end",        "Vue 3 · TypeScript · Vite · Tailwind 4 · Pinia", "écart",       BRIQUE],
    ["Éditeur",          "CodeMirror 6 · marked · DOMPurify",              "ajout",       GRIS],
    ["Back-end",         "Python 3.11+ · Flask 3 · SQLAlchemy 2",          "conforme",    VERT],
    ["Base de données",  "MySQL 8.4  (SQLite en développement et en test)","au choix",    VERT],
    ["IA",               "Ollama en local · qwen2.5:3b",                   "au choix",    VERT],
    ["Authentification", "JWT HS256 · refresh httpOnly haché, en rotation","conforme",    VERT],
    ["Tests",            "pytest · pytest-cov · Vitest",                   "ajout",       GRIS],
    ["CI / CD",          "GitHub Actions — 3 travaux parallèles",          "conforme",    VERT],
    ["Conteneurisation", "Docker Compose — MySQL, gunicorn, nginx",        "conforme",    VERT],
  ];
  pile.forEach((l, i) => {
    const y = 1.92 + i * 0.5;
    if (i % 2 === 0) s.addShape(pres.ShapeType.rect, { x: M, y, w: CW, h: 0.46, fill: { color: C.background2 }, line: { color: C.background2, width: 0.5 }, objectName: `bande ${i}` });
    s.addText(l[0], { x: M + 0.22, y, w: 2.5, h: 0.46, fontSize: 13.5, bold: true, color: C.text1, valign: "middle", margin: 0, isTextBox: true });
    s.addText(l[1], { x: M + 2.85, y, w: 7.0, h: 0.46, fontSize: 13, color: C.text1, fontFace: "Courier New", valign: "middle", margin: 0, isTextBox: true });
    s.addText(l[2].toUpperCase(), { x: 10.3, y, w: 2.4, h: 0.46, fontSize: 10.5, bold: true, color: l[3], fontFace: "Courier New", align: "right", valign: "middle", margin: 0, isTextBox: true });
  });

  s.addText([
    { text: "CONFORME", options: { bold: true, color: VERT, fontFace: "Courier New", fontSize: 10.5 } },
    { text: "  à la recommandation  ·  ", options: { color: GRIS } },
    { text: "AU CHOIX", options: { bold: true, color: VERT, fontFace: "Courier New", fontSize: 10.5 } },
    { text: "  dans une alternative ouverte par le cahier des charges  ·  ", options: { color: GRIS } },
    { text: "ÉCART", options: { bold: true, color: BRIQUE, fontFace: "Courier New", fontSize: 10.5 } },
    { text: "  assumé  ·  ", options: { color: GRIS } },
    { text: "AJOUT", options: { bold: true, color: GRIS, fontFace: "Courier New", fontSize: 10.5 } },
    { text: "  hors cahier des charges", options: { color: GRIS } },
  ], { x: M, y: 6.5, w: CW, h: 0.4, fontSize: 12, margin: 0, isTextBox: true, objectName: "legende pile" });
}

{
  const s = add("CONTENT", "Conception",
`[9:40 — 10:50]
Trois choix de technologie, et c'est sur ceux-là qu'on m'attend.
Le premier est le seul écart à la recommandation. Le cahier des charges recommande React ; j'ai retenu Vue 3. Il recommande, il n'impose pas. La Composition API donne le même modèle de composants, mon niveau de maîtrise y était nettement meilleur — et sur un projet mené seule, la maîtrise est ce qui réduit le risque. L'intégration de CodeMirror 6 y est directe. Et le découpage vues, composants, services, store reste transposable à React tel quel : le choix n'enferme personne.
Le deuxième, le cahier des charges ouvre lui-même l'alternative : OpenAI ou un modèle local. C'est l'exigence RGPD qui tranche. « Aucune donnée personnelle transmise sans anonymisation » est intenable sur des textes rédigés librement, où l'anonymisation n'est jamais exhaustive. En hébergeant qwen2.5:3b localement, les contenus ne quittent pas l'infrastructure : l'exigence est satisfaite par construction, et non par une clause de contrat. Les contreparties sont réelles — latence, qualité inférieure à GPT-4, un service de plus à maintenir. La couche ia_service isole l'appel : basculer vers un fournisseur distant ne toucherait pas les routes.
Le troisième, c'est « MySQL ou MongoDB », et j'ai écrit un argumentaire pour celui-là, parce que la compétence 8 demande des composants d'accès aux données SQL et NoSQL. Je n'ai pas ajouté de NoSQL, et ce n'est pas par difficulté — ce serait facile, et c'est précisément ce qui rend l'ajout suspect. Mes données ont un schéma stable, elles sont fortement reliées, et le volume est modeste. Surtout, les clés étrangères en ON DELETE CASCADE mettent en œuvre le droit à l'effacement du RGPD en une seule instruction ; en base documentaire, ce serait du code applicatif à écrire, à tester et à maintenir, pour une obligation légale. Un composant dont la seule justification est de figurer dans une grille est une dette technique déguisée en compétence. Je l'assume, et le jury est libre de considérer le critère comme non couvert.`);
  s.addText("Trois choix de technologie", { placeholder: "title" });
  s.addText("Un écart assumé, et deux alternatives que le cahier des charges ouvrait lui-même.", { placeholder: "lead" });

  card(s, { x: M, y: 1.95, w: 3.87, h: 4.1, badge: "écart", title: "Vue 3 plutôt que React",
    body: "Le cahier des charges recommande, il n'impose pas.\n\nMême modèle de composants ; ma maîtrise y était meilleure, et seule sur un projet la maîtrise réduit le risque.\n\nIntégration directe de CodeMirror 6.\n\nLe découpage services / store reste transposable à React." });

  card(s, { x: M + 4.11, y: 1.95, w: 3.87, h: 4.1, badge: "au choix", title: "Ollama plutôt qu'OpenAI",
    body: "Le cahier des charges autorise les deux. C'est le RGPD qui tranche.\n\nL'anonymisation n'est jamais exhaustive sur du texte libre.\n\nEn local, les contenus ne sortent pas : l'exigence est satisfaite par construction." });

  card(s, { x: M + 8.22, y: 1.95, w: 3.88, h: 4.1, badge: "au choix", title: "MySQL plutôt que MongoDB",
    body: "Schéma stable, données fortement reliées, volume modeste.\n\nLes clés étrangères en ON DELETE CASCADE mettent en œuvre le droit à l'effacement en une seule instruction." });

}

{
  const s = add("MEDIA", "Conception",
`[10:50 — 12:40]
Architecture client/serveur découplée en trois niveaux, avec un service d'inférence en périphérie.
La figure se lit de gauche à droite, et les trois numéros suivent une requête : le navigateur appelle l'API en HTTPS, les routes valident et autorisent, puis la main descend aux services et enfin à la couche d'accès aux données. Chaque dépendance est posée à la hauteur de la couche qui l'appelle — Ollama et le serveur de courriel en face des services, MySQL en face de l'accès aux données.
Le point à retenir est celui du titre : le navigateur ne dialogue jamais directement avec le moteur d'inférence. Tout passe par l'API, qui vérifie l'authentification, la propriété du document, le quota, puis journalise l'interaction.
Si le front appelait Ollama directement, ni le quota ni la traçabilité RGPD ne seraient applicables — un utilisateur contournerait le quota en appelant le port 11434 lui-même. L'intermédiaire n'est pas une commodité, c'est ce qui rend les contraintes du cahier des charges opposables.
Deuxième point : le moteur n'écoute que sur l'interface de bouclage. C'était une habitude implicite ; c'est devenu une consigne écrite après la publication de la CVE sur Ollama.
Les technologies et leurs justifications, je viens de les passer en revue : je ne reviens que sur ce qui se voit ici — le moteur d'inférence est un service en périphérie, atteint par l'API seule, et la bascule vers un fournisseur distant ne toucherait aucune route.`);
  s.addText("L'architecture logicielle", { placeholder: "title" });
  media(s, { file: `${R}/docs/dossier/fig/archi.png`, ratio: 2.28, y: 1.45, maxH: 4.9, name: "architecture" });
  s.addText("Architecture logicielle — trois niveaux et services périphériques (dossier § 5.2).", { placeholder: "caption" });
}

{
  const s = add("CONTENT", "Conception",
`[12:40 — 14:20]
Le backend est découpé en trois couches, et la règle qui compte est celle de la colonne de droite : ce que chaque couche ne contient jamais.
Aucun import Flask dans services/. Cette règle n'est pas esthétique, elle est fonctionnelle : c'est elle qui rend les composants métier testables sans démarrer de serveur ni ouvrir de base. Sans elle, tout test d'auth_service ou d'ia_service deviendrait un test d'intégration, plus lent et plus fragile. C'est le socle du plan de tests.
Je suis honnête sur une nuance, et elle est écrite dans le dossier : la lecture de la configuration passe par current_app, qui est un objet Flask. C'est le seul point où la règle fléchit, et le dossier l'explique en § 7.2.
Cinq blueprints structurent l'API : auth, documents, dossiers, IA, admin.
Côté front, la même logique : aucune vue n'appelle axios directement, tout passe par la couche services. L'intercepteur qui rafraîchit l'access token après un 401 et rejoue la requête est donc écrit une seule fois, à un seul endroit.`);
  s.addText("Le découpage en couches", { placeholder: "title" });
  s.addText("La règle d'architecture qui rend le plan de tests possible.", { placeholder: "lead" });

  const rows = [
    ["Présentation", "app/routes/",
     "Reçoit la requête HTTP et la rend présentable au reste : vérifie le jeton, contrôle le type et la longueur de chaque entrée, refuse ce qui sort des valeurs admises. Choisit le code de retour — 404 plutôt que 403, 429 plutôt que 403 — et sérialise la réponse en JSON."],
    ["Métier", "app/services/",
     "Porte les règles qui seraient vraies sans le Web : hacher un mot de passe, émettre et faire tourner un jeton, détecter un rejeu, composer un prompt et appeler le modèle, envoyer un courriel. Elle lève des exceptions ; c'est la couche au-dessus qui les traduit en codes HTTP."],
    ["Persistance", "database/db.py",
     "Décrit les données et seule elle parle au SGBD : les 8 modèles, leurs relations, les contraintes d'intégrité, et les requêtes — toutes paramétrées, y compris l'agrégation qui calcule le quota."],
  ];
  s.addText("Couche", { x: M + 0.28, y: 1.95, w: 1.9, h: 0.3, fontSize: 12, bold: true, color: THEME.colors.accent5, margin: 0, isTextBox: true });
  s.addText("Responsabilité", { x: M + 4.0, y: 1.95, w: 7.8, h: 0.3, fontSize: 12, bold: true, color: THEME.colors.accent5, margin: 0, isTextBox: true });
  rows.forEach((r, i) => {
    const y = 2.28 + i * 1.22;
    bloc(s, { x: M, y, w: CW, h: 1.12, fill: C.background2, name: `couche ${r[0]}` });
    s.addText(r[0], { x: M + 0.28, y: y + 0.14, w: 3.5, h: 0.34, fontSize: 15, bold: true, color: C.text1, margin: 0, isTextBox: true });
    s.addText(r[1], { x: M + 0.28, y: y + 0.5, w: 3.5, h: 0.34, fontSize: 12.5, color: THEME.colors.accent5, fontFace: "Courier New", margin: 0, isTextBox: true });
    s.addText(r[2], { x: M + 4.0, y: y + 0.12, w: 7.8, h: 1.0, fontSize: 12.5, color: C.text1, lineSpacing: 15, valign: "top", margin: 0, isTextBox: true });
  });
  s.addText("Côté front, la même règle : aucune vue n'appelle axios. L'intercepteur qui rejoue une requête après un 401 est donc écrit une seule fois.",
    { x: M, y: 6.06, w: CW, h: 0.5, fontSize: 13, color: THEME.colors.accent5, margin: 0, isTextBox: true, objectName: "note front" });
}

{
  const s = add("MEDIA", "Conception",
`[14:20 — 15:25]
Le maquettage a produit neuf planches, une par écran, construites en trois temps : recensement des écrans à partir du périmètre, charte graphique et composants, puis les planches elles-mêmes. Chaque planche porte sa route, sa garde de routeur, et une colonne « intentions » numérotée.
Plutôt que la planche, je montre l'écran livré — c'est lui qui prouve que l'intention a été tenue. L'éditeur est l'écran le plus représentatif du produit.
Trois choses à relever. La barre d'outils Markdown, et les trois modes d'affichage à droite : écrire, partagé, lire. La mention « enregistré automatiquement » sous le titre, qui se déclenche 2,5 secondes après la dernière frappe — je montrerai le code. Et le bouton IA, qui ouvre l'assistant.
Le maquettage a servi deux objectifs : vérifier la couverture du périmètre, et fixer les intentions avant d'écrire la moindre ligne de Vue. Les planches sont en annexe § 12.1, les captures en § 12.2.`);
  s.addText("L'éditeur de document", { placeholder: "title" });
  media(s, { file: `${R}/docs/captures/C-08-editeur-document.png`, ratio: 1.3, y: 1.45, maxH: 4.9, name: "capture editeur" });
  s.addText("Capture C-08 — éditeur de document, écran livré (dossier § 12.2). Neuf planches de maquettage l'ont précédé (§ 12.1).", { placeholder: "caption" });
}

{
  // Cette diapositive affichait la figure « enchaînement des écrans ». Le
  // diagramme est dense : réduit à la largeur utile, ses libellés devenaient
  // illisibles au vidéoprojecteur. Il est redessiné ici en quatre bandes, une
  // par niveau d'accès, avec les routes et les gardes telles qu'elles sont
  // déclarées dans frontend/src/index.ts.
  const s = add("CONTENT", "Conception",
`[15:25 — 16:20]
Seize routes, et trois gardes qui découpent l'application en trois zones : le public, l'espace authentifié, le back-office.
La première bande, ce sont les pages ouvertes à tous : l'accueil, la vitrine, les pages légales. Aucune garde.
La deuxième est publique elle aussi, mais réservée au visiteur : connexion, inscription, mot de passe oublié. La garde guestOnly renvoie au tableau de bord quelqu'un qui est déjà connecté — sans elle, un utilisateur connecté pourrait rouvrir le formulaire de connexion.
La troisième est l'espace personnel, derrière requiresAuth : sans jeton, retour à la connexion.
La quatrième est le back-office, et elle cumule les deux gardes. Le rôle est relu dans le store, qui le tient de l'API — pas du jeton.
Je précise tout de suite, parce que c'est la question qu'on pose : ces gardes sont du confort d'usage. Elles évitent d'afficher un écran vide et masquent le menu d'administration. Le contrôle qui compte est côté serveur, et je le montrerai dans la partie sécurité.`);
  s.addText("Les zones d'accès et les gardes du routeur", { placeholder: "title" });
  s.addText("Seize routes déclarées dans frontend/src/index.ts, et un seul beforeEach pour les trois gardes.", { placeholder: "lead" });

  const zones = [
    ["Public", "ouvert à tous", "aucune",
     "/   ·   /fonctionnalites   ·   /tarifs   ·   /modeles\n/mentions-legales   ·   /cgu   ·   /confidentialite"],
    ["Public — visiteur seul", "déjà connecté → /dashboard", "guestOnly",
     "/login   ·   /register   ·   /forgot-password   ·   /reset-password"],
    ["Espace authentifié", "sans jeton → /login", "requiresAuth",
     "/dashboard   ·   /documents\n/documents/nouveau   ·   /documents/:id"],
    ["Back-office", "rôle ≠ admin → /dashboard", "requiresAuth + requiresAdmin",
     "/admin"],
  ];

  zones.forEach((z, i) => {
    const y = 1.92 + i * 1.1;
    bloc(s, { x: M, y, w: CW, h: 1.02, fill: C.background2, name: `zone ${z[0]}` });

    s.addText(z[0], { x: M + 0.26, y: y + 0.15, w: 2.3, h: 0.34, fontSize: 14.5, bold: true, color: C.text1, margin: 0, isTextBox: true });
    s.addText(z[1], { x: M + 0.26, y: y + 0.52, w: 2.4, h: 0.34, fontSize: 10, color: THEME.colors.accent5, fontFace: "Courier New", margin: 0, isTextBox: true });

    // La garde, dans une pastille encadrée : c'est le mot que le jury cherche.
    s.addShape(pres.ShapeType.rect, { x: 3.15, y: y + 0.24, w: 2.35, h: 0.54, fill: { color: C.background1 }, line: { ...BORD }, objectName: `garde ${z[2]}` });
    s.addText(z[2], { x: 3.18, y: y + 0.24, w: 2.29, h: 0.54, fontSize: z[2].length > 20 ? 9.5 : 11.5, bold: true, color: THEME.colors.accent1, fontFace: "Courier New", align: "center", valign: "middle", margin: 0, isTextBox: true });

    s.addText(z[3], { x: 5.75, y: y + 0.13, w: 6.72, h: 0.78, fontSize: 11.5, color: C.text1, fontFace: "Courier New", lineSpacing: 16, valign: "middle", margin: 0, isTextBox: true });
  });

  s.addText([
    { text: "Ces trois gardes sont du confort d'usage. ", options: { bold: true, color: THEME.colors.accent1 } },
    { text: "Elles évitent un écran vide et masquent le menu d'administration. Le contrôle qui compte est côté serveur — § 8.", options: { color: THEME.colors.accent5 } },
  ], { x: M, y: 6.38, w: CW, h: 0.45, fontSize: 13, margin: 0, isTextBox: true, objectName: "avertissement gardes" });
}

{
  const s = add("MEDIA", "Conception",
`[16:20 — 17:20]
Le modèle conceptuel. Huit entités, et les cardinalités portées par les associations.
Trois choix à défendre.
Les identifiants sont des UUID v4, pas des entiers auto-incrémentés. Conséquence directe sur la sécurité : les identifiants ne sont pas énumérables. On ne balaie pas /documents/1, /documents/2.
Les cascades sont déclarées au niveau du SGBD, pas seulement dans l'ORM. Si quelqu'un supprime une ligne avec un client SQL, l'intégrité tient quand même. Une contrainte qui n'existe que dans le code applicatif n'est pas une contrainte.
La table ia journalise chaque interaction avec le contenu avant et après. Elle sert trois choses à la fois : l'historique affiché dans l'éditeur, le calcul du quota par agrégation, et la traçabilité RGPD. C'est la même donnée qui rend les trois possibles.
Relevez « Contient » entre dossier et document, en 0,1 côté document : un document peut n'appartenir à aucun dossier. C'est le cas que le ON DELETE SET NULL doit produire quand un dossier est supprimé.`);
  s.addText("Le modèle conceptuel de données", { placeholder: "title" });
  media(s, { file: `${R}/docs/dossier/fig/mcd.png`, ratio: 1.608, y: 1.45, maxH: 4.9, name: "modele conceptuel de donnees" });
  s.addText("Modèle conceptuel de données (dossier § 5.4).", { placeholder: "caption" });
}

{
  const s = add("MEDIA", "Conception",
`[17:20 — 18:15]
Le modèle logique, c'est-à-dire le même modèle une fois les associations résolues en clés étrangères — en bleu sur la figure.
Deux choses à relever.
Toutes les clés étrangères convergent vers user : c'est la traduction, dans le schéma, du cloisonnement par compte. Sessions, documents, dossiers, appels IA, consentements, demandes de réinitialisation — chaque ligne appartient à quelqu'un, et c'est la base qui le sait, pas seulement le code.
La table ia porte deux clés étrangères, id_document et user_id. Le document aurait suffi pour retrouver son propriétaire, mais le quota se calcule par agrégation sur l'utilisateur : la redondance est assumée, elle évite une jointure sur chaque appel.
Le modèle physique est en § 5.4 et le script de création MySQL en § 5.5 — il a été exécuté et vérifié sur un serveur réel.`);
  s.addText("Le modèle logique de données", { placeholder: "title" });
  media(s, { file: `${R}/docs/dossier/fig/mld.png`, ratio: 1.572, y: 1.45, maxH: 4.9, name: "modele logique de donnees" });
  s.addText("Modèle logique de données (dossier § 5.4) ; modèle physique et script MySQL en § 5.4 et § 5.5.", { placeholder: "caption" });
}

{
  const s = add("MEDIA", "Conception",
`[18:15 — 19:00]
Trois acteurs, et une bande par acteur : c'est la bande qui porte le périmètre, ce qui évite de tirer un trait vers chacun des dix-huit cas.
Le périmètre de l'utilisateur est strictement limité à ses propres documents et dossiers, ses trois actions IA dans la limite de son quota, et son historique. À l'intérieur de sa bande, les cas sont groupés par thème : mes documents, l'assistance IA, ma session. L'administrateur hérite de tout ce qui précède et ajoute le back-office.
En bas, deux cas à part : vérifier le quota et s'authentifier. Aucun acteur ne les déclenche lui-même — ils sont inclus par les cas qui en dépendent, et la liste de ces cas est écrite sous l'ovale plutôt que tirée en flèches.
Le moteur d'inférence apparaît comme un système externe sollicité par l'API — jamais par le navigateur, c'est la cohérence avec l'architecture.
Le cas le plus significatif est la génération d'une assistance IA : c'est celui que je détaille en diagramme de séquence, et c'est aussi celui sur lequel porte mon jeu d'essai.`);
  s.addText("Les cas d'utilisation", { placeholder: "title" });
  media(s, { file: `${R}/docs/dossier/fig/usecase.png`, ratio: 1.855, y: 1.45, maxH: 4.9, name: "cas d'utilisation" });
  s.addText("Diagramme des cas d'utilisation (dossier § 5.6).", { placeholder: "caption" });
}

{
  const s = add("MEDIA", "Conception",
`[19:00 — 20:30]
Le diagramme de séquence du cas le plus significatif : la génération d'une assistance IA.
Suivez l'ordre des contrôles, il n'est pas arbitraire. Authentification, puis propriété du document, puis validation des entrées, puis quota — et seulement ensuite l'appel au modèle. Chaque contrôle est placé avant celui qui coûte plus cher. Vérifier le quota après l'inférence aurait permis de consommer le moteur sans jamais être compté.
Lisez les numéros, et surtout les étapes 12 et 17. L'entrée du journal est créée AVANT l'appel au modèle, et pas après : c'est elle qui fournit l'identifiant que la réponse renvoie au client, et dont il se sert ensuite pour signaler l'insertion. Si le modèle ne répond pas, cette entrée est annulée — un échec ne coûte donc aucun quota. Le test TI-50 l'exige explicitement.
Le cas d'erreur est traité : si Ollama ne répond pas, la couche ia_service traduit l'exception réseau en un message lisible, et aucune ligne n'est écrite dans le journal — sinon un échec consommerait du quota.
Et la décision finale reste à l'utilisateur : rien n'est appliqué au document automatiquement. C'est à la fois une exigence d'ergonomie et une mesure de sécurité — ne jamais appliquer automatiquement la sortie d'un modèle.`);
  s.addText("Le diagramme de séquence — génération IA", { placeholder: "title" });
  media(s, { file: `${R}/docs/dossier/fig/seq-uc10.png`, ratio: 1.852, y: 1.45, maxH: 4.9, name: "diagramme de sequence" });
  s.addText("Séquence — génération d'une assistance IA (dossier § 5.7).", { placeholder: "caption" });
}

// ═══════════════════════════ 5. Réalisation ═══════════════════════════

pres.addSection({ title: "Réalisation" });

{
  const s = add("SECTION", "Réalisation",
`[20:30 — 20:40]
« Quatrième temps : la réalisation, avec les écrans et le code. »`);
  s.addText("4", { placeholder: "num" });
  s.addText("La réalisation", { placeholder: "title" });
  s.addText("Dossier § 6 — spécifications techniques  ·  § 7 — écrans et extraits de code", { placeholder: "sub" });
}

{
  // Vue d'ensemble des écrans livrés. Les captures n'ont pas toutes le même
  // rapport : les pages entières (accueil, tableau de bord) sont bien plus
  // hautes que les captures de fenêtre. Les vignettes de
  // docs/captures/vignettes/ sont rognées PAR LE HAUT au rapport de la case —
  // un recadrage centré ferait disparaître l'en-tête des pages longues. Elles
  // se régénèrent avec la commande donnée dans docs/soutenance/README.md.
  const s = add("MEDIA", "Réalisation",
`[20:40 — 21:30]
Avant d'entrer dans le code, la série complète des écrans livrés. Onze écrans, douze captures — l'accueil figure deux fois, en version large et en version mobile, parce que l'adaptation aux petits écrans fait partie des exigences.
La première ligne est la zone publique et les pages réservées au visiteur : accueil, accueil mobile, connexion, inscription, mot de passe oublié, réinitialisation.
La seconde est l'espace authentifié puis le back-office : tableau de bord, liste des documents, nouveau document, éditeur, assistant IA, administration. C'est le découpage que je vous ai montré sur les gardes du routeur.
Ces douze captures sont en annexe § 12.2, et chacune y est accompagnée du code qui la produit. Je m'arrête maintenant sur trois d'entre elles et sur leur code.`);
  s.addText("Les écrans livrés", { placeholder: "title" });

  const vignettes = [
    ["C-01-accueil", "C-01 Accueil"],
    ["C-01b-accueil-mobile", "C-01b Mobile"],
    ["C-02-connexion", "C-02 Connexion"],
    ["C-03-inscription", "C-03 Inscription"],
    ["C-04-mot-de-passe-oublie", "C-04 Mot de passe"],
    ["C-11-reinitialisation", "C-11 Réinitialisation"],
    ["C-05-tableau-de-bord", "C-05 Tableau de bord"],
    ["C-06-liste-documents", "C-06 Mes documents"],
    ["C-07-nouveau-document", "C-07 Nouveau document"],
    ["C-08-editeur-document", "C-08 Éditeur"],
    ["C-09-assistant-ia", "C-09 Assistant IA"],
    ["C-10-back-office", "C-10 Back-office"],
  ];

  const VW = 1.8667, VH = 1.45, PAS = 2.0467;
  vignettes.forEach((v, i) => {
    const x = M + (i % 6) * PAS;
    const y = 2.05 + Math.floor(i / 6) * 2.0;
    s.addImage({
      path: `${R}/docs/captures/vignettes/${v[0]}.png`,
      x, y, w: VW, h: VH,
      objectName: `vignette ${v[0]}`,
    });
    s.addShape(pres.ShapeType.rect, { x, y, w: VW, h: VH, fill: { type: "none" }, line: { ...BORD }, objectName: `cadre ${v[0]}` });
    s.addText(v[1], { x, y: y + VH + 0.04, w: VW, h: 0.26, fontSize: 9.5, color: THEME.colors.accent5, fontFace: "Courier New", align: "center", margin: 0, isTextBox: true });
  });

  s.addText("Ligne 1 : zone publique et pages réservées au visiteur.  ·  Ligne 2 : espace authentifié, puis back-office.",
    { x: M, y: 6.1, w: CW, h: 0.35, fontSize: 13, color: THEME.colors.accent5, margin: 0, isTextBox: true, objectName: "legende zones" });
  s.addText("Captures d'interfaces (dossier § 12.2) — chacune est accompagnée du code correspondant.", { placeholder: "caption" });
}

{
  const s = add("SPLIT", "Réalisation",
`[21:30 — 22:25]
Le tableau de bord, capture réelle de l'application en fonctionnement.
Trois compteurs en haut, puis trois portes d'entrée vers la rédaction. Ce choix répond à un constat d'usage : devant un éditeur vide, l'utilisateur qui n'a pas de structure en tête abandonne. Proposer un modèle ou un document existant supprime la page blanche.
Techniquement, deux choses. Les compteurs viennent de l'API, pas d'un calcul côté client. Et la recherche filtre la page courante côté client, parce que la pagination est serveur : la liste n'est jamais chargée entièrement.
Huit captures figurent en annexe § 12.2, avec le code correspondant.`);
  s.addText("Le tableau de bord", { placeholder: "title" });
  s.addText([
    ...li([
      "Trois compteurs — documents créés, brouillons, finalisés — servis par l'API, jamais recalculés côté client.",
      "Trois portes d'entrée : page blanche, modèle, document existant. Devant un éditeur vide, l'utilisateur sans structure en tête abandonne.",
      "Pagination serveur : la liste n'est jamais chargée entièrement ; la recherche filtre la page courante.",
      "État vide explicite plutôt qu'une zone muette.",
      "Huit captures figurent en annexe § 12.2, avec le code qui les produit.",
    ]),
  ], { placeholder: "body" });
  bloc(s, { x: 7.52, y: 1.5, w: 4.66, h: 4.9, fill: "FFFFFF", name: "cadre capture C-05" });
  s.addImage({ path: `${R}/docs/captures/C-05-tableau-de-bord.png`, x: 7.52, y: 1.5, w: 4.66, h: 4.9, objectName: "capture C-05" });
  s.addText("Capture C-05 — tableau de bord.", { placeholder: "caption" });
}

{
  const s = add("SPLIT", "Réalisation",
`[22:25 — 24:00]
L'éditeur, l'écran central du produit.
Je m'arrête sur l'enregistrement automatique, parce que quatre décisions tiennent dans quelques lignes.
Le délai de 2,5 secondes n'est pas arbitraire : enregistrer à chaque caractère saturerait l'API et multiplierait les écritures ; un délai trop long rendrait la sauvegarde invisible et ferait perdre du travail.
Le minuteur précédent est systématiquement annulé — sans ça, une frappe rapide empilerait les requêtes.
L'enregistrement différé est doublé d'un bouton explicite : l'utilisateur doit pouvoir forcer la sauvegarde.
Et rien n'est enregistré tant que le titre est vide.
Une remarque de méthode, que j'ai tenu à écrire dans le dossier : sur la capture C-07, l'indicateur d'enregistrement n'apparaît pas, parce qu'aucune frappe n'a eu lieu. En conclure que la fonctionnalité est absente serait une erreur. Une capture atteste d'un état, pas d'un comportement — vérifier une fonctionnalité demande de lire le code ou d'exécuter un scénario. C'est exactement la raison d'être du jeu d'essai.`);
  s.addText("L'éditeur et l'enregistrement automatique", { placeholder: "title" });
  s.addText([
    ...li([
      "2,5 s : enregistrer à chaque caractère saturerait l'API ; un délai trop long ferait perdre du travail.",
      "Le minuteur précédent est annulé à chaque frappe — sinon les requêtes s'empilent.",
      "Doublé d'un bouton explicite : l'utilisateur garde la main.",
      "Rien n'est enregistré tant que le titre est vide.",
      "Une capture atteste d'un état, pas d'un comportement — d'où le jeu d'essai du § 10.",
    ]),
  ], { placeholder: "body" });
  bloc(s, { x: 7.3, y: 2.1, w: 5.4, h: 4.15, fill: "FFFFFF", name: "cadre capture C-07" });
  s.addImage({ path: `${R}/docs/captures/C-07-nouveau-document.png`, x: 7.3, y: 2.1, w: 5.4, h: 4.15, objectName: "capture C-07" });
  s.addText("Capture C-07 — éditeur, création d'un document.", { placeholder: "caption" });
}

{
  const s = add("CONTENT", "Réalisation",
`[24:00 — 25:50]
Un composant métier : le quota IA. Dix lignes, et trois décisions.
Première décision : c'est une agrégation. Je compte les lignes du journal des appels sur les vingt-quatre dernières heures. Je ne lis pas un compteur stocké sur l'utilisateur. Un compteur se désynchronise — il suffit d'un échec entre l'appel et l'incrément ; une agrégation est toujours juste par construction.
Deuxième décision : c'est une fenêtre glissante, pas un compteur journalier. Le cahier des charges dit « 20 requêtes par 24 heures », pas « par jour calendaire ». Avec un compteur remis à zéro à minuit, un utilisateur fait quarante appels entre 23 h et 1 h.
Troisième décision : le code de retour est 429, Too Many Requests, pas 403. Un 403 dit « vous n'avez pas le droit » ; un 429 dit « réessayez plus tard ». Ce n'est pas la même information pour le client.
Et le contrôle est entièrement côté serveur. Le front affiche le quota restant, mais c'est de l'affichage.
Le test correspondant est le cas JE-07 du jeu d'essai, et mes données de test contiennent une ligne datée de 25 heures précisément pour vérifier la fenêtre glissante.`);
  s.addText("Un composant métier — le quota IA", { placeholder: "title" });
  s.addText("Contrôlé côté serveur, avant tout appel au modèle (dossier § 7.2).", { placeholder: "lead" });

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
    ["Une fenêtre glissante", "Le cahier des charges dit « 20 requêtes par 24 heures », pas « par jour ». Avec un compteur remis à zéro à minuit, on fait 20 appels à 23 h et 20 autres à 1 h : 40 en deux heures, sans jamais dépasser la règle. La fenêtre part donc de l'instant présent, moins 24 heures."],
    ["429, pas 403", "« Réessayez plus tard », et non « vous n'avez pas le\u00A0droit\u00A0»."],
  ];
  const hauteurs = [0.52, 1.30, 0.42];   // le point du milieu porte l'explication
  let yp = 1.95;
  pts.forEach((p, i) => {
    s.addText(p[0], { x: 8.2, y: yp, w: 4.5, h: 0.34, fontSize: 15, bold: true, color: THEME.colors.accent1, margin: 0, isTextBox: true });
    s.addText(p[1], { x: 8.2, y: yp + 0.36, w: 4.5, h: hauteurs[i], fontSize: 13.5, color: C.text1, valign: "top", margin: 0, isTextBox: true, lineSpacing: 16 });
    yp += 0.36 + hauteurs[i] + 0.42;
  });
}

{
  const s = add("CONTENT", "Réalisation",
`[25:50 — 26:45]
Un composant d'accès aux données, et c'est le motif le plus répété du projet.
La propriété est dans la clause WHERE. Je ne charge pas le document puis ne compare son propriétaire : je demande à la base un document qui a cet identifiant ET qui appartient à l'utilisateur courant.
La différence n'est pas stylistique. Avec un contrôle a posteriori, il suffit d'oublier un if dans une route pour ouvrir une faille. Ici, oublier la condition fait échouer le test de propriété, qui existe pour chaque ressource.
Conséquence voulue : un identifiant qui appartient à quelqu'un d'autre renvoie 404, pas 403. Un 403 confirmerait que la ressource existe. Le 404 est indiscernable d'un identifiant inexistant.
Et toutes les requêtes passent par l'ORM, paramétrées, sans aucune concaténation de chaîne. C'est l'objectif de qualité que je m'étais fixé et il est tenu sans exception.`);
  s.addText("Un composant d'accès aux données", { placeholder: "title" });
  s.addText("Le motif répété pour chaque ressource de l'application (dossier § 7.3).", { placeholder: "lead" });

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

{
  const s = add("CONTENT", "Réalisation",
`[26:45 — 27:55]
Dernier point de la réalisation : l'application est conteneurisée, intégrée en continu depuis le 4 octobre, et la pile a été exécutée. Pas seulement décrite — jouée, le 5 octobre sur un démon Docker réel, et de nouveau depuis sur mon poste.
La composition compte trois services. MySQL 8.4 avec un volume persistant et une sonde de santé — sans la sonde, le backend démarre avant que la base accepte les connexions. Le backend tourne sous Gunicorn, pas sous le serveur de développement de Flask, avec un utilisateur non privilégié. Le frontend est construit par Vite en deux étapes puis servi par Nginx : l'image finale pèse 82,9 mégaoctets mesurés, parce qu'elle ne contient que des fichiers statiques et pas la chaîne de construction.
Un détail qui compte : les secrets sont déclarés sous la forme dollar-accolade VAR deux-points point d'interrogation message. La composition échoue immédiatement si la variable manque, au lieu de démarrer avec une valeur inventée.
Ollama reste hors composition, sur l'hôte, atteint par host.docker.internal : son image pèse plusieurs gigaoctets et le modèle se télécharge à part.
La CI tourne à chaque push et chaque pull request, en trois travaux parallèles. Le parallélisme n'est pas une optimisation de performance : enchaînés, un échec du frontend masquait l'état du backend et il fallait deux exécutions pour connaître les deux.
La troisième carte est la liste de contrôle d'une mise en ligne : passer APP_ENV à production, une clé distincte, CORS_ORIGINS au domaine réel, TLS devant l'application. Ce sont des valeurs de configuration, pas des développements — l'application est prête à être hébergée le jour où on lui donne un domaine.`);
  s.addText("La conteneurisation et l'intégration continue", { placeholder: "title" });
  s.addText("Trois services, trois travaux de CI, et une liste de contrôle pour une mise en ligne (dossier § 6).", { placeholder: "lead" });

  card(s, { x: M, y: 1.95, w: 3.87, h: 3.15, badge: "3×", title: "Conteneurisation",
    body: "MySQL 8.4 — volume persistant, sonde de santé.\n\nBackend — Gunicorn, utilisateur non privilégié.\n\nFrontend — build Vite, servi par Nginx, 82,9 Mo." });
  card(s, { x: M + 4.11, y: 1.95, w: 3.87, h: 3.15, badge: "CI", title: "Intégration continue",
    body: "GitHub Actions à chaque push et chaque pull request, en trois travaux parallèles : backend (Ruff, pytest), frontend (ESLint, vue-tsc, Vitest, build), Docker (composition et images).\n\nEnchaînés, un échec du frontend masquait l'état du backend." });
  card(s, { x: M + 8.22, y: 1.95, w: 3.88, h: 3.15, badge: "→", accent: THEME.colors.accent4, title: "Le jour d'une mise en ligne",
    body: "APP_ENV=production, qui active Secure sur le cookie.\nUne JWT_SECRET_KEY distincte.\nCORS_ORIGINS au domaine réel.\nCompte MySQL sans droits DDL.\nTLS devant l'application.\nRedis pour le limiteur de débit." });

  s.addText("Ollama reste hors composition, sur l'hôte : son image pèse plusieurs gigaoctets et le modèle se télécharge à part.",
    { x: M, y: 5.45, w: CW, h: 0.4, fontSize: 13, color: THEME.colors.accent5, margin: 0, isTextBox: true, objectName: "note ollama" });
}

// ═══════════════════════════ 6. Sécurité ═══════════════════════════

pres.addSection({ title: "Sécurité" });

{
  const s = add("SECTION", "Sécurité",
`[27:55 — 28:05]
« Cinquième temps : la sécurité. C'est le fil rouge du projet, pas un chapitre. »`);
  s.addText("5", { placeholder: "num" });
  s.addText("La sécurité", { placeholder: "title" });
  s.addText("Dossier § 8 — OWASP Top 10, sessions, contrôle d'accès, validation", { placeholder: "sub" });
}

{
  const s = add("CONTENT", "Sécurité",
`[28:05 — 30:05]
Ma grille de lecture est l'OWASP Top 10 2021, croisée avec les exigences du cahier des charges et les recommandations de l'ANSSI. Le dossier traite les dix catégories ; j'en montre six.
Le point de méthode d'abord : la sécurité n'a pas été traitée en fin de projet, et pas par vertu — par nécessité pratique. Le filtrage par propriétaire dans le WHERE, le stockage d'empreintes, le refus de démarrer sans clé : ce sont des choix de structure. Les ajouter après coup aurait demandé de réécrire les couches concernées.
A01, je viens de le montrer : la propriété est dans le WHERE, et le rôle est relu en base, pas lu dans le jeton.
A02 : bcrypt avec sel pour les mots de passe, SHA-256 pour les jetons. Aucun secret en clair en base — une fuite de la base ne permet pas de rejouer une session.
A05 : l'application refuse de démarrer sans JWT_SECRET_KEY. Pas de valeur par défaut, pas de repli silencieux. Une clé de secours en dur est une clé en production.
A10 : la seule URL sortante du projet est OLLAMA_URL, une valeur de configuration. Aucune entrée utilisateur ne devient jamais une destination HTTP.
Je suis transparente sur une faiblesse, elle est dans le dossier : A09, la journalisation applicative est incomplète. Le journal des interactions IA existe, mais il n'y a pas de journalisation systématique des événements de sécurité.`);
  s.addText("Les risques OWASP et leur traitement", { placeholder: "title" });
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
`[30:05 — 32:20]
Le cycle de vie des sessions, parce que c'est la partie du projet qui m'a demandé le plus de réflexion.
Deux besoins contradictoires. Un jeton court est sûr mais oblige à se reconnecter sans arrêt. Un jeton long est confortable mais dangereux. La combinaison des deux donne les deux propriétés : un access token de quinze minutes, non révocable mais à fenêtre d'exposition courte ; un refresh token de sept jours, révocable côté serveur.
Le refresh token vit dans un cookie httpOnly, SameSite Strict, limité au chemin /auth. Inaccessible au JavaScript : même une faille XSS ne permet pas de le lire.
Et ce que je stocke en base n'est pas le jeton, c'est son empreinte SHA-256. Une fuite de la base ne permet pas de rejouer une session.
Le code à droite est le cœur du mécanisme. À chaque usage, le jeton présenté est marqué consommé et un nouveau est émis. Si un jeton déjà consommé se représente, il n'y a que deux explications : soit l'utilisateur rejoue une vieille requête, soit quelqu'un a volé le jeton. Dans le doute, je révoque toutes les sessions du compte. C'est volontairement brutal — la gêne est un reconnexion, le risque évité est un compte compromis.
Dernier point, et c'est celui qu'on oublie le plus souvent : à la réinitialisation du mot de passe, toutes les sessions sont supprimées. Changer son mot de passe après une compromission ne sert à rien si les sessions ouvertes par l'attaquant survivent.
Une précision sur la purge : la tâche purge_expired_sessions filtre sur l'expiration du jeton, pas sur le drapeau revoke. Une session révoquée doit survivre jusqu'au terme de son jeton — sinon un jeton volé puis rejoué ne serait plus reconnu comme un rejeu, et la détection de vol tomberait.`);
  s.addText("Le cycle de vie des sessions", { placeholder: "title" });
  s.addText("Deux besoins contradictoires, résolus par deux jetons de nature différente (dossier § 8).", { placeholder: "lead" });

  const el = [
    ["Access token", "JWT HS256, 15 minutes, en-tête Authorization, jamais stocké en base."],
    ["Refresh token", "64 octets tirés au hasard, déposés dans un cookie httpOnly : le JavaScript de la page ne peut pas le lire, donc une faille XSS ne suffit pas à le voler. SameSite=Strict écarte les requêtes venues d'un autre site, et path=/auth fait qu'il n'est envoyé qu'aux deux routes qui en ont besoin. Il vit 7 jours, et reste révocable à tout instant — c'est lui qui rend la déconnexion réelle."],
    ["Stockage", "Empreinte SHA-256 uniquement : une fuite de la base ne permet pas de rejouer une session."],
  ];
  const hb = [1.0, 2.05, 1.05];          // le refresh token porte l'explication
  let ye = 1.95;
  el.forEach((e, i) => {
    bloc(s, { x: M, y: ye, w: 6.1, h: hb[i], fill: C.background2, name: `session ${e[0]}` });
    s.addText(e[0], { x: M + 0.28, y: ye + 0.14, w: 5.5, h: 0.32, fontSize: 15.5, bold: true, color: THEME.colors.accent1, margin: 0, isTextBox: true });
    s.addText(e[1], { x: M + 0.28, y: ye + 0.5, w: 5.54, h: hb[i] - 0.62, fontSize: 13.5, color: C.text1, valign: "top", margin: 0, isTextBox: true, lineSpacing: 16 });
    ye += hb[i] + 0.18;
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
Les chiffres, rejoués le 4 novembre : 461 cas automatisés, tous au vert — 403 côté backend, 58 côté frontend. 95 % de couverture backend, avec 100 % sur auth_service et sur email_service, et 93 à 97 % sur les routes. Le chiffre est calculé hors jeu_essai.py, qui est un script de peuplement et non du code applicatif ; en l'incluant, la couverture tombe à 90 %.
Mon objectif de couverture était 80 % sur services/ et sur les routes, sans objectif chiffré ailleurs. C'est volontaire : viser un pourcentage global pousse à écrire des tests faciles sur du code sans risque. Les 55 % du front sont tirés vers le bas par six modules de service qui sont des enveloppes d'une ligne autour d'axios — les tester reviendrait à tester axios.
Trois zones concentrent l'effort : la chaîne d'authentification, le contrôle de propriété, et le quota. Ce sont les trois endroits où une régression coûte cher.
Le quatrième niveau, les tests système, a été joué le 5 octobre sur la pile conteneurisée : sept cas au vert sur dix. Un échec réel sur le parcours de réinitialisation de mot de passe, et deux cas hors de portée de cet environnement, dont celui qui demande un Ollama joignable. Restent les tests de charge, qui viennent après.`);
  s.addText("Le plan de tests et ses résultats", { placeholder: "title" });
  s.addText("Campagne rejouée le 4 novembre 2026 — quatre niveaux, du moins coûteux au plus coûteux à exécuter.", { placeholder: "lead" });

  stat(s, { x: M, y: 1.9, w: 2.9, h: 1.3, value: "461", label: "cas automatisés, tous au vert" });
  stat(s, { x: M + 3.07, y: 1.9, w: 2.9, h: 1.3, value: "403", label: "backend  ·  58 frontend" });
  stat(s, { x: M + 6.14, y: 1.9, w: 2.9, h: 1.3, value: "95 %", label: "couverture backend" });
  stat(s, { x: M + 9.21, y: 1.9, w: 2.89, h: 1.3, value: "100 %", label: "sur la chaîne d'authentification" });

  const niv = [
    ["Analyse statique", "vue-tsc, Ruff", "à chaque push"],
    ["Tests unitaires", "pytest, Vitest", "à chaque push"],
    ["Tests d'intégration", "pytest + client Flask", "à chaque push"],
    ["Tests fonctionnels", "cahier de tests manuel", "fin d'itération"],
  ];
  niv.forEach((v, i) => {
    const x = M + i * 3.07;
    bloc(s, { x, y: 3.45, w: i === 3 ? 2.89 : 2.9, h: 1.55, fill: C.background2, name: `niveau ${v[0]}` });
    s.addText(v[0], { x: x + 0.22, y: 3.62, w: 2.46, h: 0.5, fontSize: 15, bold: true, color: C.text1, margin: 0, isTextBox: true });
    s.addText(v[1], { x: x + 0.22, y: 4.14, w: 2.46, h: 0.34, fontSize: 13, color: THEME.colors.accent5, margin: 0, isTextBox: true });
    s.addText(v[2], { x: x + 0.22, y: 4.5, w: 2.46, h: 0.34, fontSize: 12.5, bold: true, color: THEME.colors.accent3, fontFace: "Courier New", margin: 0, isTextBox: true });
  });

  s.addText("Trois zones concentrent l'effort : la chaîne d'authentification, le contrôle de propriété et le quota — les trois endroits où une régression coûte cher.",
    { x: M, y: 5.3, w: CW, h: 0.5, fontSize: 14, color: THEME.colors.accent5, margin: 0, isTextBox: true, objectName: "zones d effort" });
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
  s.addText("Le jeu d'essai", { placeholder: "title" });
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
Je décris d'abord le dispositif, parce que c'est lui qu'on évalue — les trouvailles viennent après.
Concrètement : chaque matin, une revue avec Claude. Je lui donne la pile que j'ai retenue et les versions réellement résolues — pas les plages déclarées, les versions résolues — et il confronte cet état aux avis publiés la veille. Ce que ça m'apporte, c'est le balayage : seule, je n'aurais pas relu tous les jours les avis de quinze bibliothèques. Ce que ça ne remplace pas, c'est le verdict : savoir si une CVE est exploitable ICI demande de connaître la configuration, et c'est moi qui tranche. Le journal garde la trace des deux.
Trois périmètres, chacun avec ses sources et son rythme. Les dépendances : la base d'avis de GitHub et les audits des gestionnaires de paquets, consultés à chaque installation puis revus chaque semaine. La sécurité applicative : NVD et CVE.org, les alertes CISA, l'OWASP Top 10, les bulletins du CERT-FR — chaque semaine. Le réglementaire : la CNIL, la Commission européenne, numerique.gouv.fr — chaque mois, parce que ces textes bougent plus lentement.
Le principe directeur est une règle de tri : je ne retiens une entrée que si le composant figure dans requirements.txt, dans package.json ou dans l'environnement d'exécution. Surveiller l'actualité de la sécurité en général produit du bruit ; surveiller ce que le projet utilise réellement produit des décisions. Et chaque entrée se termine par un verdict d'applicabilité — ma version est-elle dans la plage affectée, et les conditions d'exploitation sont-elles réunies ici ? C'est ce verdict qui distingue une veille d'une collection de liens.
Huit entrées sur six mois, trois ont appelé une action. C'est la mesure de l'utilité de l'exercice.
Si on me demande les trouvailles : DOMPurify, 5,1 — la bibliothèque que j'avais ajoutée pour corriger une faille XSS en portait une elle-même ; mise à jour en 3.4.16. Ollama, 9,1 — atténuée parce que le serveur n'écoute que sur localhost ; mise à jour quand même. L'AI Act, entré en application le 2 août 2026, après le cahier des charges. Et axios, le 31 mars : deux versions piégées publiées après la compromission d'un compte mainteneur npm, projet non affecté, et c'est le package-lock.json commité qui permet de le prouver après coup.
Le premier constat est que la sévérité publiée ne prédit pas l'impact réel. La CVE la plus sévère de ma liste, 9,1 sur Ollama, était atténuée par ma configuration — le serveur n'écoutait que sur localhost. La plus modérée, 5,1 sur DOMPurify, affectait directement ma version.
DOMPurify est l'entrée la plus instructive, parce que c'est la bibliothèque que j'avais ajoutée précisément pour corriger une faille XSS. Découvrir qu'elle porte elle-même une vulnérabilité de contournement établit un principe : une mesure de sécurité est un composant comme un autre, avec sa propre surface d'attaque. Ajouter une bibliothèque d'assainissement ne clôt pas le sujet XSS, elle le déplace vers la maintenance de cette bibliothèque. D'où la valeur de la défense en profondeur : je stocke du Markdown brut, pas du HTML — si DOMPurify échoue, la donnée stockée n'est toujours pas exécutable.
Ollama éclaire rétrospectivement mon choix d'architecture : héberger soi-même, c'est aussi maintenir soi-même. La décision reste la bonne au regard du RGPD, mais elle se paie en maintenance, et le dire est plus honnête que de la présenter comme un choix sans contrepartie.
Et l'AI Act justifie à lui seul la veille comme livrable : le cahier des charges, rédigé avant l'entrée en application, ne mentionne que le RGPD. Sans ce suivi, j'aurais livré une application non conforme à une obligation entrée en vigueur trois semaines avant la fin du développement.`);
  s.addText("Ma veille — une revue tous les matins", { placeholder: "title" });
  s.addText("Un rituel quotidien outillé, braqué sur la pile que j'ai choisie. Journal : docs/veille/journal-de-veille.md", { placeholder: "lead" });

  card(s, { x: M, y: 1.9, w: 5.9, h: 2.2, badge: "le rituel", title: "Chaque matin, une revue assistée",
    body: "J'ai mis en place une revue quotidienne avec Claude : il reprend les technologies que j'ai retenues, confronte les versions réellement résolues du projet aux avis publiés la veille, et me rend une liste courte. Lui fait le balayage, moi le verdict." });

  card(s, { x: M + 6.2, y: 1.9, w: 5.9, h: 2.2, badge: "le tri", title: "Ce qui vaut la peine d'être retenu",
    body: "Je ne retiens une entrée que si le composant figure dans requirements.txt, dans package.json ou dans ce qui tourne. Et chaque entrée finit par un verdict : ma version est-elle dans la plage affectée, et les conditions d'exploitation réunies ici ?" });

  s.addText("CE QUI PASSE EN REVUE", { x: M, y: 4.30, w: 5.9, h: 0.26, fontSize: 11, bold: true, color: THEME.colors.accent5, charSpacing: 1.2, margin: 0, isTextBox: true });
  [["Back-end", "Flask, Werkzeug, SQLAlchemy, PyJWT, bcrypt, requests, WeasyPrint, Gunicorn, PyMySQL"],
   ["Front-end", "Vue, Vite, DOMPurify, marked, CodeMirror, axios, Tailwind"],
   ["Exécution", "Ollama et le modèle, MySQL, les images Docker"],
   ["Cadre", "OWASP Top 10 et LLM Top 10, CERT-FR, AI Act, CNIL, RGAA"]].forEach((l, i) => {
    const y = 4.60 + i * 0.50;
    s.addText(l[0], { x: M, y, w: 1.25, h: 0.46, fontSize: 13, bold: true, color: THEME.colors.accent1, valign: "top", margin: 0, isTextBox: true });
    s.addText(l[1], { x: M + 1.3, y, w: 4.6, h: 0.46, fontSize: 12.5, color: C.text1, valign: "top", margin: 0, lineSpacing: 15, isTextBox: true });
  });

  s.addText("CE QUE ÇA A MAINTENU À JOUR", { x: M + 6.2, y: 4.30, w: 5.9, h: 0.26, fontSize: 11, bold: true, color: THEME.colors.accent5, charSpacing: 1.2, margin: 0, isTextBox: true });
  [["03/11/26", "DOMPurify porté en 3.4.17", "cinq contournements publiés en 2026 sur la bibliothèque qui assainit le Markdown"],
   ["03/10/26", "Werkzeug épinglé en 3.1.9", "la veille a montré que les dépendances transitives n'étaient pas gelées : deux verrous à empreintes les figent"],
   ["10/10/26", "AI Act entré au périmètre", "applicable depuis le 02/08/26, après le cahier des charges"],
   ["31/03/26", "axios vérifié, non affecté", "compte mainteneur npm compromis ; c'est le fichier de verrouillage qui le prouve"]].forEach((l, i) => {
    const y = 4.60 + i * 0.50;
    s.addText(l[0], { x: M + 6.2, y, w: 0.92, h: 0.46, fontSize: 11.5, color: THEME.colors.accent5, fontFace: "Courier New", valign: "top", margin: 0, isTextBox: true });
    s.addText([{ text: l[1] + " — ", options: { bold: true, color: THEME.colors.accent1 } },
               { text: l[2], options: {} }],
      { x: M + 7.18, y, w: 4.92, h: 0.46, fontSize: 12.5, color: C.text1, valign: "top", margin: 0, lineSpacing: 15, isTextBox: true });
  });

  s.addText("Reste ouvert, et je le dis : les CVE Ollama, que ma configuration atténue sans les corriger — le moteur n'écoute que sur la boucle locale.",
    { x: M, y: 6.62, w: CW, h: 0.4, fontSize: 12.5, color: THEME.colors.accent5, margin: 0, isTextBox: true, objectName: "reste ouvert" });
}

{
  // Diapositive de clôture : on reprend les QUATRE OBJECTIFS du cahier des
  // charges dans les mêmes termes qu'à la diapositive 4, pour que la fin
  // réponde mot pour mot à l'ouverture, et on adosse à chacun la mesure de
  // sécurité qui le tient.
  const s = add("CLOSE", "Tests, veille et bilan",
`[38:30 — 40:00]
Pour conclure, je reprends les quatre objectifs du cahier des charges, dans les termes mêmes où je vous les ai présentés en ouverture, et je dis pour chacun ce qui le tient.
Rédiger et stocker : l'éditeur Markdown, le CRUD complet, les dossiers, et l'enregistrement automatique deux secondes et demie après la dernière frappe.
Suggérer et reformuler : les trois commandes — reformuler, corriger, compléter — un quota de vingt appels par vingt-quatre heures compté par agrégation, et chaque interaction journalisée avec l'avant et l'après.
Un espace sécurisé : deux jetons, un court et un long révocable, et le cloisonnement par compte écrit dans la clause WHERE de chaque requête.
Se conformer : le RGPD obtenu par l'architecture puisque les contenus ne sortent pas, l'accessibilité RGAA vérifiée sur quinze écrans sans aucune violation axe-core, et la traçabilité AI Act enregistrée en base.
À droite, les six mesures de sécurité qui tiennent tout cela. Je les reprends vite, parce que chacune a déjà été montrée.
La propriété est dans la clause WHERE, et une ressource qui ne vous appartient pas renvoie 404 — pas 403, qui confirmerait son existence. Le rôle est relu en base à chaque requête, jamais lu dans le jeton. Les mots de passe sont en bcrypt salé, les jetons stockés en empreinte SHA-256 : une fuite de la base ne permet pas de rejouer une session. L'application refuse de démarrer sans sa clé de signature. Le refresh token est dans un cookie inaccessible au JavaScript, et rejouer un jeton déjà consommé révoque tout le compte. Enfin je stocke du Markdown brut et non du HTML : si DOMPurify échoue un jour, la donnée stockée n'est toujours pas exécutable.
Si vous me demandez ce qui manque : la journalisation des événements de sécurité est incomplète, c'est la catégorie A09 de l'OWASP, et c'est écrit dans le dossier.
Je vous remercie, je suis à votre disposition pour vos questions.`);
  s.addText("Le bilan au regard du cahier des charges", { placeholder: "title" });

  // ── Les quatre objectifs du cahier des charges ────────────────────
  s.addText("LES QUATRE OBJECTIFS DU CAHIER DES CHARGES", {
    x: M, y: 1.62, w: 7.3, h: 0.3, fontSize: 11, bold: true, color: ACCENT_SOMBRE,
    fontFace: "Courier New", charSpacing: 2, margin: 0, isTextBox: true,
  });

  const objectifs = [
    ["Rédiger et stocker", "Éditeur Markdown, CRUD, dossiers, enregistrement automatique"],
    ["Suggérer et reformuler", "Trois commandes, quota 20 / 24 h, chaque appel journalisé"],
    ["Un espace sécurisé", "Deux jetons, sessions révocables, cloisonnement par compte"],
    ["Se conformer", "RGPD par l'architecture, RGAA 0 violation, AI Act tracé en base"],
  ];
  objectifs.forEach((o, i) => {
    const y = 2.02 + i * 0.92;
    s.addShape(pres.ShapeType.rect, { x: M, y: y + 0.08, w: 0.34, h: 0.34, fill: { color: "5FBF8F" }, line: { color: "5FBF8F", width: 1 }, objectName: `coche ${i}` });
    s.addText("✓", { x: M, y: y + 0.08, w: 0.34, h: 0.34, fontSize: 15, bold: true, color: "111111", align: "center", valign: "middle", margin: 0, isTextBox: true });
    s.addText(o[0], { x: M + 0.52, y, w: 6.7, h: 0.34, fontSize: 17, bold: true, color: "F4F1EA", margin: 0, isTextBox: true });
    s.addText(o[1], { x: M + 0.52, y: y + 0.36, w: 6.7, h: 0.46, fontSize: 13.5, color: "A8A194", margin: 0, isTextBox: true });
  });

  // ── Les mesures de sécurité ───────────────────────────────────────
  s.addShape(pres.ShapeType.rect, { x: 8.3, y: 1.52, w: 4.4, h: 4.26, fill: { color: "111111" }, line: { color: "F4F1EA", width: 1.25 }, objectName: "cadre securite" });
  s.addText("LA SÉCURITÉ, EN SIX POINTS", {
    x: 8.58, y: 1.78, w: 3.84, h: 0.3, fontSize: 11, bold: true, color: ACCENT_SOMBRE,
    fontFace: "Courier New", charSpacing: 2, margin: 0, isTextBox: true,
  });

  const securite = [
    "La propriété est dans le WHERE — 404, jamais 403",
    "Le rôle est relu en base, jamais dans le jeton",
    "bcrypt salé ; jetons stockés en empreinte SHA-256",
    "Refus de démarrer sans JWT_SECRET_KEY",
    "Refresh httpOnly ; un rejeu révoque le compte",
    "Markdown brut stocké, jamais de HTML",
  ];
  securite.forEach((t, i) => {
    const y = 2.22 + i * 0.58;
    s.addText("—", { x: 8.58, y, w: 0.26, h: 0.3, fontSize: 13, bold: true, color: ACCENT_SOMBRE, valign: "top", margin: 0, isTextBox: true });
    s.addText(t, { x: 8.9, y, w: 3.56, h: 0.52, fontSize: 12.5, color: "F4F1EA", lineSpacing: 15, valign: "top", margin: 0, isTextBox: true });
  });

  s.addText("Merci de votre attention.", { x: M, y: 6.0, w: 7.3, h: 0.6, fontSize: 24, bold: true, color: ACCENT_SOMBRE, margin: 0, isTextBox: true, objectName: "merci" });
}

{
  // Diapositive de bonus, APRÈS le remerciement : elle ne compte pas dans les
  // quarante minutes. Elle existe pour le moment où le jury demande à voir
  // l'application, et pour la projection d'attente avant l'exposé.
  //
  // La vidéo est EMBARQUÉE dans le fichier : le .pptx devient autonome, sans
  // chemin à conserver le jour J. L'affiche est ce que montrent les lecteurs
  // qui ne jouent pas la vidéo — l'export PDF, notamment.
  const s = add("CLOSE", "Tests, veille et bilan",
`[hors minutage]
Diapositive de secours, à ne pas montrer pendant l'exposé.
Elle sert à deux moments. Avant de commencer, en projection d'attente pendant que le jury s'installe. Et après les questions, si on vous demande à voir l'application tourner : une minute douze, du premier écran au back-office.
La vidéo est embarquée dans le fichier : rien à brancher, aucun chemin à retrouver. Un clic sur l'image la lance.
Si le lecteur du jour refuse de la jouer, le fichier est aussi dans le dépôt, sous docs/soutenance/demo-pub-helpmedraft.mp4, et le PDF de secours en montre l'affiche.`);
  s.addText("La démonstration", { placeholder: "title" });

  bloc(s, { x: 2.03, y: 1.56, w: 9.24, h: 5.2, fill: "111111", line: { color: "F4F1EA", width: 1.25 }, name: "cadre video" });
  s.addMedia({
    type: "video",
    path: `${R}/docs/soutenance/demo-pub-helpmedraft.mp4`,
    // `cover` attend l'image encodée, pas un chemin.
    cover: "data:image/png;base64," + require("fs").readFileSync(`${R}/docs/soutenance/affiche-demo.png`).toString("base64"),
    x: 2.03, y: 1.56, w: 9.24, h: 5.2,
    objectName: "video demonstration",
  });
}

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  // pptxgenjs nomme ses médias « image-16-1.png » ; PowerPoint écrit
  // « image1.png ». Le fichier est valide dans les deux cas, mais des lecteurs
  // simplifiés réconcilient les médias sur leur nom plutôt que sur la
  // relation, et affichent alors la même image sur plusieurs diapositives.
  require("child_process").execFileSync("python3",
    ["-I", `${__dirname}/normaliser-pptx.py`, OUT], { stdio: "inherit" });
  console.log(`écrit : ${OUT} — ${n} diapositives`);
})();
