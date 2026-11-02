/**
 * Tests de non-régression de l'assainissement du Markdown — TSEC-01 à TSEC-05.
 *
 * Reprise de `frontend/test_xss.mjs`, qui imprimait l'avant et l'après sans
 * rien vérifier : lu par un humain attentif, il faisait le travail ; dans une
 * CI, il passait toujours.
 *
 * La chaîne testée est exactement celle de `MarkdownEditor.vue` :
 *   marked.parse(contenu, options)  →  DOMPurify.sanitize(html, profil html)
 *
 * `marked` convertit le Markdown en HTML mais laisse passer le HTML brut
 * qu'il contient ; comme le rendu est injecté par `v-html`, c'est DOMPurify
 * qui constitue la seule barrière contre le XSS stocké.
 *
 * MÉTHODE — les assertions portent sur le DOM produit, jamais sur la chaîne
 * HTML. Une recherche de « onload » dans le texte échouerait sur une charge
 * que `marked` a échappée en `&lt;svg/onload=…&gt;` : la sous-chaîne est
 * toujours là, mais c'est devenu du texte inerte, pas un attribut. Ce qui
 * compte n'est pas l'absence du mot, c'est l'absence d'élément exécutable.
 */
import DOMPurify from "dompurify";
import { marked } from "marked";
import { describe, expect, it } from "vitest";

const markedOptions = {
  gfm: true,
  breaks: true,
  headerIds: false,
  mangle: false,
} as const;

function rendre(markdown: string): string {
  const htmlBrut = marked.parse(markdown, markedOptions) as string;
  return DOMPurify.sanitize(htmlBrut, { USE_PROFILES: { html: true } });
}

/** Rend le Markdown puis le parse comme le ferait `v-html`. */
function rendreEnDom(markdown: string): HTMLElement {
  const conteneur = document.createElement("div");
  conteneur.innerHTML = rendre(markdown);
  return conteneur;
}

/** Tout attribut de la forme `on*` porté par un élément du rendu. */
function gestionnairesEvenement(racine: HTMLElement): string[] {
  return [...racine.querySelectorAll("*")].flatMap((element) =>
    [...element.attributes]
      .filter((attribut) => attribut.name.toLowerCase().startsWith("on"))
      .map((attribut) => `${element.tagName.toLowerCase()}[${attribut.name}]`),
  );
}

/** Toute URL exécutable portée par un href ou un src. */
function urlsDangereuses(racine: HTMLElement): string[] {
  return [...racine.querySelectorAll("[href], [src]")]
    .map((e) => e.getAttribute("href") ?? e.getAttribute("src") ?? "")
    .filter((url) => /^\s*(javascript|data:text\/html|vbscript)/i.test(url));
}

describe("assainissement du rendu Markdown", () => {
  it("TSEC-01 · neutralise un gestionnaire d'événement sur une image", () => {
    const rendu = rendreEnDom('<img src=x onerror="alert(1)">');
    expect(gestionnairesEvenement(rendu)).toEqual([]);
  });

  it("TSEC-02 · supprime une balise script", () => {
    const rendu = rendreEnDom("<script>alert(1)</script>");
    expect(rendu.querySelector("script")).toBeNull();
  });

  it("TSEC-03 · neutralise un lien à protocole javascript", () => {
    const rendu = rendreEnDom('<a href="javascript:alert(1)">clic</a>');
    expect(urlsDangereuses(rendu)).toEqual([]);
  });

  it("TSEC-04 · ne laisse aucun élément SVG exécutable", () => {
    const rendu = rendreEnDom("<svg/onload=alert(1)>");
    expect(gestionnairesEvenement(rendu)).toEqual([]);
    expect(rendu.querySelector("svg")).toBeNull();
  });

  it("supprime une iframe pointant vers un site tiers", () => {
    const rendu = rendreEnDom(
      '<iframe src="https://exemple-malveillant.test"></iframe>',
    );
    expect(rendu.querySelector("iframe")).toBeNull();
  });

  it.each([
    ["gestionnaire sur body", '<body onload="alert(1)">'],
    ["champ auto-focalisé", '<input onfocus="alert(1)" autofocus>'],
    ["bascule de details", '<details open ontoggle="alert(1)">x</details>'],
    ["objet embarqué", '<object data="javascript:alert(1)"></object>'],
    ["balise embed", '<embed src="javascript:alert(1)">'],
    [
      "form action",
      '<form action="javascript:alert(1)"><button>ok</button></form>',
    ],
    [
      "svg imbriqué",
      '<svg><a xlink:href="javascript:alert(1)"><text>clic</text></a></svg>',
    ],
    ["casse mélangée", '<IMG SRC=x OnErRoR="alert(1)">'],
  ])("neutralise aussi : %s", (_nom, charge) => {
    const rendu = rendreEnDom(charge);
    expect(gestionnairesEvenement(rendu)).toEqual([]);
    expect(urlsDangereuses(rendu)).toEqual([]);
  });

  it("une charge échappée reste du texte, pas un élément", () => {
    // Le mot « onload » peut subsister dans le texte affiché sans danger :
    // ce qui compte est qu'aucun élément ne le porte comme attribut.
    const rendu = rendreEnDom("<svg/onload=alert(1)>");
    expect(rendu.textContent).toContain("onload");
    expect(gestionnairesEvenement(rendu)).toEqual([]);
  });

  it("TSEC-05 · préserve le Markdown légitime", () => {
    const rendu = rendreEnDom(
      "# Titre\n\n**gras** *italique*\n\n- un\n- deux\n\n[lien](https://exemple.fr)\n\n`code`",
    );

    expect(rendu.querySelector("h1")?.textContent).toBe("Titre");
    expect(rendu.querySelector("strong")?.textContent).toBe("gras");
    expect(rendu.querySelector("em")?.textContent).toBe("italique");
    expect(rendu.querySelectorAll("li")).toHaveLength(2);
    expect(rendu.querySelector("code")?.textContent).toBe("code");

    const lien = rendu.querySelector("a");
    expect(lien?.getAttribute("href")).toBe("https://exemple.fr");
    expect(lien?.textContent).toBe("lien");
  });

  it("préserve un tableau GitHub Flavored Markdown", () => {
    const rendu = rendreEnDom("| a | b |\n|---|---|\n| 1 | 2 |");
    expect(rendu.querySelector("table")).not.toBeNull();
    expect(rendu.querySelectorAll("td")).toHaveLength(2);
  });

  it("affiche comme du texte un extrait de code parlant de balises", () => {
    // Un document professionnel peut légitimement citer du HTML.
    const rendu = rendreEnDom(
      "La balise `<script>` sert à charger du JavaScript.",
    );
    expect(rendu.querySelector("script")).toBeNull();
    expect(rendu.querySelector("code")?.textContent).toBe("<script>");
  });
});
