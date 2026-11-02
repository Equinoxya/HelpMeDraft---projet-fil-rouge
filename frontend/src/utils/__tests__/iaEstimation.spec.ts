import { describe, it, expect } from "vitest";
import {
  JETONS_PAR_SECONDE,
  estimerDureeGeneration,
  formaterDuree,
  avancementEstime,
} from "../iaEstimation";

describe("estimerDureeGeneration", () => {
  it("croît avec la longueur du texte", () => {
    // Le temps d'inférence est proportionnel au nombre de jetons à produire :
    // c'est l'hypothèse sur laquelle repose toute l'estimation. Si elle est
    // violée, le compteur affiché n'a plus aucun sens.
    const court = estimerDureeGeneration("a".repeat(200), "reformuler");
    const long = estimerDureeGeneration("a".repeat(3000), "reformuler");
    expect(long).toBeGreaterThan(court);
  });

  it("annonce une attente plausible pour la borne de contenu du backend", () => {
    // IA_MAX_CONTENU_LENGTH vaut 3 000 caractères côté backend. Au débit
    // plancher de 15 jetons/s, cela représente une petite minute. Ce test
    // verrouille l'ordre de grandeur : une estimation de 5 s ou de 5 min
    // signalerait une erreur de calcul, pas un réglage.
    const secondes = estimerDureeGeneration("a".repeat(3000), "reformuler");
    expect(secondes).toBeGreaterThan(20);
    expect(secondes).toBeLessThan(180);
  });

  it("annonce moins de temps pour compléter que pour reformuler", () => {
    // Compléter ne produit qu'une suite, pas une réécriture du texte entier.
    // L'estimer comme une reformulation annoncerait environ le double du
    // temps réellement passé.
    const texte = "a".repeat(2000);
    expect(estimerDureeGeneration(texte, "completer")).toBeLessThan(
      estimerDureeGeneration(texte, "reformuler"),
    );
  });

  it("ne renvoie jamais zéro, même pour un texte vide", () => {
    // Une estimation nulle ferait diviser par zéro dans la barre de
    // progression et afficherait « 0 s » pendant toute la génération.
    expect(estimerDureeGeneration("", "corriger")).toBeGreaterThanOrEqual(1);
  });

  it("utilise un débit strictement positif", () => {
    // Le débit vient d'une variable d'environnement : une valeur absente ou
    // mal saisie ne doit pas produire une estimation infinie.
    expect(JETONS_PAR_SECONDE).toBeGreaterThan(0);
  });
});

describe("formaterDuree", () => {
  it("affiche les secondes en dessous d'une minute", () => {
    expect(formaterDuree(45)).toBe("45 s");
  });

  it("garde les secondes au-delà de la minute", () => {
    // « 1 min » figé pendant soixante secondes ressemble à un blocage : c'est
    // le chiffre qui bouge qui prouve que la génération avance.
    expect(formaterDuree(85)).toBe("1 min 25 s");
  });

  it("omet les secondes quand elles sont nulles", () => {
    expect(formaterDuree(120)).toBe("2 min");
  });

  it("ne produit pas de durée négative", () => {
    expect(formaterDuree(-5)).toBe("0 s");
  });
});

describe("avancementEstime", () => {
  it("progresse proportionnellement au temps écoulé", () => {
    expect(avancementEstime(10, 40)).toBeCloseTo(0.25);
  });

  it("ne dépasse jamais 95 % même très au-delà de l'estimation", () => {
    // Une barre à 100 % alors que la génération continue fait croire à un
    // blocage : c'est exactement le problème que le compteur doit éviter.
    expect(avancementEstime(600, 40)).toBe(0.95);
  });

  it("vaut zéro si l'estimation est nulle", () => {
    expect(avancementEstime(10, 0)).toBe(0);
  });
});
