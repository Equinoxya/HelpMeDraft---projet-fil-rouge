import api from "./api";
import type {
  GenererIaPayload,
  GenererIaResponse,
  IaHistoriqueEntry,
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

export default { generer, historique };
