export interface DossierItem {
  id_dossier: string;
  name: string;
  created_at: string;
  document_count: number;
}
export interface CreateDossierPayload {
  name: string;
}
