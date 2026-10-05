import api from "./api";

/**
 * Récupère l'archive des données personnelles du compte connecté
 * (RGPD art. 15 et 20) et déclenche son enregistrement.
 *
 * POURQUOI PASSER PAR UN BLOB, et non par un simple `<a href>` : la requête est
 * authentifiée par l'en-tête `Authorization`, qu'un lien ne porte pas. Un lien
 * recevrait donc un 401. C'est le script qui demande l'archive, puis provoque
 * l'enregistrement.
 */
export async function telechargerMesDonnees(): Promise<string> {
  const reponse = await api.get<Blob>("/auth/export", {
    responseType: "blob",
  });

  // Le serveur propose un nom construit sur la date. On le lit dans l'en-tête
  // plutôt que de le reconstruire ici : deux endroits qui fabriquent le même nom
  // finissent par ne plus être d'accord. Le repli couvre le cas où un
  // intermédiaire masque l'en-tête.
  const disposition = reponse.headers["content-disposition"] ?? "";
  const trouve = /filename="([^"]+)"/.exec(disposition);
  const nomFichier = trouve?.[1] ?? "helpmedraft-export.zip";

  const url = URL.createObjectURL(reponse.data);
  try {
    const lien = document.createElement("a");
    lien.href = url;
    lien.download = nomFichier;
    lien.click();
  } finally {
    // Sans cette libération, le navigateur garde l'archive entière en mémoire
    // jusqu'au rechargement de la page.
    URL.revokeObjectURL(url);
  }

  return nomFichier;
}

export default { telechargerMesDonnees };
