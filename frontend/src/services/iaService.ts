import api from "./api";
import type {
  GenererIaPayload,
  GenererIaResponse,
  IaHistoriqueEntry,
  MarquerInsertionResponse,
} from "../types/ia";

/**
 * Lance une génération.
 *
 * `signal` permet à l'appelant d'abandonner l'attente. Il n'est pas optionnel
 * par confort : aucun délai ne borne plus l'inférence côté serveur, donc sans
 * moyen d'annuler, une génération lente laisserait l'utilisateur sans aucune
 * porte de sortie.
 */
async function generer(
  idDocument: string,
  payload: GenererIaPayload,
  signal?: AbortSignal,
): Promise<GenererIaResponse> {
  const response = await api.post<GenererIaResponse>(
    `/documents/${idDocument}/ia/generer`,
    payload,
    { signal },
  );
  return response.data;
}

async function historique(idDocument: string): Promise<IaHistoriqueEntry[]> {
  const response = await api.get<IaHistoriqueEntry[]>(
    `/documents/${idDocument}/ia/historique`,
  );
  return response.data;
}

/**
 * Marque une proposition comme versée au document (AI Act, art. 50).
 *
 * Appelée APRÈS la modification du contenu local, jamais avant : marquer une
 * insertion qui n'a pas eu lieu produirait une trace fausse, ce qui est pire
 * qu'une trace absente.
 *
 * La route est idempotente côté serveur, donc un rejeu après coupure réseau ne
 * réécrit pas l'horodatage d'origine.
 */
async function marquerInsertion(
  idDocument: string,
  idIa: string,
  positionDebut: number,
): Promise<MarquerInsertionResponse> {
  const response = await api.post<MarquerInsertionResponse>(
    `/documents/${idDocument}/ia/${idIa}/insertion`,
    { position_debut: positionDebut },
  );
  return response.data;
}

export default { generer, historique, marquerInsertion };
