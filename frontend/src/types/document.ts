// frontend/src/types/document.ts
export type DocumentFormat = "markdown" | "wysiwyg";
export type DocumentStatus = "brouillon" | "a_relire" | "termine";

export interface DocumentItem {
  id_document: string;
  titre: string;
  content: string | null;
  format: DocumentFormat;
  status: DocumentStatus;
  id_dossier: string | null;
  created_at: string;
  updated_at: string;
}

export interface DocumentListResponse {
  items: DocumentItem[];
  page: number;
  per_page: number;
  total: number;
}

export interface DocumentListParams {
  page?: number;
  per_page?: number;
  id_dossier?: string;
}

export interface CreateDocumentPayload {
  titre: string;
  content?: string;
  format?: DocumentFormat;
  id_dossier?: string;
}

export interface UpdateDocumentPayload {
  titre?: string;
  content?: string;
  format?: DocumentFormat;
  id_dossier?: string | null;
}
export interface DocumentStatsResponse {
  total: number;
  brouillon: number;
  a_relire: number;
  termine: number;
}
