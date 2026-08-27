import api from "./api";
import type {
  GenererIaPayload,
  GenererIaResponse,
  IaHistoriqueEntry,
} from "../types/ia";

async function generer(
  idDocument: string,
  payload: GenererIaPayload,
): Promise<GenererIaResponse> {
  const response = await api.post<GenererIaResponse>(
    `/documents/${idDocument}/ia/generer`,
    payload,
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
