import { describe, it, expect } from "vitest";
import { messageErreur, estAnnulation } from "../erreurs";

describe("messageErreur", () => {
  it("préfère le message que l'API renvoie", () => {
    const err = { response: { data: { error: "Quota IA quotidien atteint" } } };
    expect(messageErreur(err, "repli")).toBe("Quota IA quotidien atteint");
  });

  it("se replie quand la réponse n'a pas la forme attendue", () => {
    // Le cas qui comptait : avec `any`, lire err.response.data.error sur ces
    // valeurs donnait « undefined » affiché tel quel à l'utilisateur.
    for (const err of [
      null,
      undefined,
      "une chaîne",
      new Error("panne réseau"),
      { response: null },
      { response: { data: null } },
      { response: { data: {} } },
      { response: { data: { error: 42 } } },
    ]) {
      expect(messageErreur(err, "repli")).toBe("repli");
    }
  });
});

describe("estAnnulation", () => {
  it("reconnaît les deux formes qu'Axios emploie", () => {
    expect(estAnnulation({ code: "ERR_CANCELED" })).toBe(true);
    expect(estAnnulation({ name: "CanceledError" })).toBe(true);
  });

  it("ne confond pas une vraie erreur avec une annulation", () => {
    expect(estAnnulation(new Error("panne"))).toBe(false);
    expect(estAnnulation({ code: "ECONNABORTED" })).toBe(false);
    expect(estAnnulation(null)).toBe(false);
  });
});
