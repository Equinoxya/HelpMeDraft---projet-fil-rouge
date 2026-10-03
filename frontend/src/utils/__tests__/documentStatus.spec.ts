/**
 * Tests unitaires de la présentation des statuts — TU-F01, TU-F02.
 */
import { describe, expect, it } from "vitest";

import type { DocumentStatus } from "../../types/document";
import { getStatusStyle, statusLabels } from "../documentStatus";

const STATUTS: DocumentStatus[] = ["brouillon", "a_relire", "termine"];

describe("statusLabels", () => {
  it("TU-F02 · associe un libellé français à chacun des trois statuts", () => {
    expect(statusLabels).toEqual({
      brouillon: "Brouillon",
      a_relire: "À relire",
      termine: "Terminé",
    });
  });

  it("couvre exactement les statuts du modèle, sans manque ni surplus", () => {
    // Si un statut est ajouté côté serveur sans l'être ici, l'interface
    // afficherait une valeur vide : ce test le signale.
    expect(Object.keys(statusLabels).sort()).toEqual([...STATUTS].sort());
  });
});

describe("getStatusStyle", () => {
  it.each(STATUTS)(
    "TU-F01 · rend une classe non vide pour « %s »",
    (statut) => {
      expect(getStatusStyle(statut)).toBeTruthy();
    },
  );

  it("distingue visuellement les trois statuts", () => {
    const styles = STATUTS.map(getStatusStyle);
    expect(new Set(styles).size).toBe(3);
  });

  it("définit toujours une couleur de fond et une couleur de texte", () => {
    for (const statut of STATUTS) {
      const style = getStatusStyle(statut);
      expect(style, statut).toMatch(/bg-/);
      expect(style, statut).toMatch(/text-/);
    }
  });
});
