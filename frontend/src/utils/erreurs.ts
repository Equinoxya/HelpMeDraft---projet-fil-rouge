/**
 * Extraction du message d'erreur d'un appel à l'API.
 *
 * POURQUOI CE MODULE EXISTE
 *
 * Le même bloc était recopié dans sept gestionnaires `catch`, chacun typé
 * `err: any` :
 *
 *     } catch (err: any) {
 *       errorMessage.value = err.response?.data?.error ?? "...";
 *     }
 *
 * `any` désactive toute vérification de type : si la forme de la réponse
 * d'erreur changeait côté backend, le compilateur ne dirait rien et l'interface
 * afficherait « undefined ». Le paramètre est ici `unknown`, ce qui oblige à
 * vérifier la forme avant de lire quoi que ce soit — c'est exactement la
 * garantie qu'on attend d'un code en TypeScript.
 */

/** Vrai si la valeur ressemble à une erreur Axios portant un message serveur. */
function aUnMessageServeur(
  err: unknown,
): err is { response: { data: { error: string } } } {
  if (typeof err !== "object" || err === null) return false;
  const reponse = (err as { response?: unknown }).response;
  if (typeof reponse !== "object" || reponse === null) return false;
  const donnees = (reponse as { data?: unknown }).data;
  if (typeof donnees !== "object" || donnees === null) return false;
  return typeof (donnees as { error?: unknown }).error === "string";
}

/**
 * Message de l'API si elle en fournit un, sinon le repli fourni par l'appelant.
 *
 * Le repli n'a pas de valeur par défaut : un message générique commun à tout
 * l'écran n'aide personne. Chaque appelant sait ce que l'utilisateur essayait
 * de faire.
 */
export function messageErreur(err: unknown, repli: string): string {
  return aUnMessageServeur(err) ? err.response.data.error : repli;
}

/**
 * Vrai si la requête a été abandonnée par l'appelant (AbortController).
 *
 * Une annulation n'est pas une panne : l'utilisateur sait ce qu'il a fait, et
 * lui afficher un message d'erreur le laisserait croire à un défaut.
 */
export function estAnnulation(err: unknown): boolean {
  if (typeof err !== "object" || err === null) return false;
  const e = err as { code?: unknown; name?: unknown };
  return e.code === "ERR_CANCELED" || e.name === "CanceledError";
}

/**
 * Vrai si l'erreur porte ce code de statut HTTP.
 *
 * Distinguer un 404 d'une panne permet d'écrire « ce document est
 * introuvable » plutôt qu'un message générique qui n'aide personne.
 */
export function estStatut(err: unknown, statut: number): boolean {
  if (typeof err !== "object" || err === null) return false;
  const reponse = (err as { response?: unknown }).response;
  if (typeof reponse !== "object" || reponse === null) return false;
  return (reponse as { status?: unknown }).status === statut;
}
