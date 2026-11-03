// frontend/src/services/documentService.ts
import api from "./api";
import type {
  DocumentItem,
  DocumentListResponse,
  DocumentListParams,
  CreateDocumentPayload,
  UpdateDocumentPayload,
  DocumentStatsResponse,
} from "../types/document";

async function list(
  params: DocumentListParams = {},
): Promise<DocumentListResponse> {
  const response = await api.get<DocumentListResponse>("/documents", {
    params,
  });
  return response.data;
}

async function get(id: string): Promise<DocumentItem> {
  const response = await api.get<DocumentItem>(`/documents/${id}`);
  return response.data;
}

async function create(payload: CreateDocumentPayload): Promise<DocumentItem> {
  const response = await api.post<DocumentItem>("/documents", payload);
  return response.data;
}

async function update(
  id: string,
  payload: UpdateDocumentPayload,
): Promise<DocumentItem> {
  const response = await api.put<DocumentItem>(`/documents/${id}`, payload);
  return response.data;
}

async function remove(id: string): Promise<void> {
  await api.delete(`/documents/${id}`);
}
async function stats(): Promise<DocumentStatsResponse> {
  const response = await api.get<DocumentStatsResponse>("/documents/stats");
  return response.data;
}

/**
 * Télécharge un document terminé au format PDF et rend le nom du fichier reçu.
 *
 * Le serveur refuse les documents non terminés par un 409 : la restriction est
 * une règle métier, pas une affaire d'interface, et l'URL est devinable. Les
 * boutons ne s'affichent donc que sur les documents terminés, mais c'est le
 * serveur qui tranche.
 */
async function exporterPdf(id: string): Promise<string> {
  const reponse = await api.get<Blob>(`/documents/${id}/export.pdf`, {
    responseType: "blob",
  });

  // Le nom est lu dans l'en-tête plutôt que reconstruit ici : deux endroits qui
  // fabriquent le même nom finissent par ne plus être d'accord. Même choix que
  // donneesPersonnellesService. `filename*` est préféré quand il est présent,
  // car lui seul porte les accents ; le repli couvre le cas où un intermédiaire
  // masque l'en-tête.
  const disposition = reponse.headers["content-disposition"] ?? "";
  const etoile = /filename\*=UTF-8''([^;]+)/.exec(disposition);
  const simple = /filename="([^"]+)"/.exec(disposition);
  const nomFichier = etoile
    ? decodeURIComponent(etoile[1])
    : (simple?.[1] ?? "document.pdf");

  const url = URL.createObjectURL(reponse.data);
  const lien = document.createElement("a");
  lien.href = url;
  lien.download = nomFichier;
  try {
    // Le lien est attaché au document le temps du clic. Chromium s'en passe,
    // mais plusieurs navigateurs ont exigé un élément présent dans l'arbre pour
    // honorer `download`, et le coût de la précaution est nul.
    lien.style.display = "none";
    document.body.appendChild(lien);
    lien.click();
  } finally {
    lien.remove();
    // Sans cette libération, le navigateur garde le PDF entier en mémoire
    // jusqu'au rechargement de la page.
    URL.revokeObjectURL(url);
  }

  return nomFichier;
}

export default {
  list,
  get,
  create,
  update,
  remove,
  stats,
  exporterPdf,
};
