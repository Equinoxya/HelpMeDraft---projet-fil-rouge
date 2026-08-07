// frontend/src/services/documentService.ts
import api from "./api";
import type {
  DocumentItem,
  DocumentListResponse,
  DocumentListParams,
  CreateDocumentPayload,
  UpdateDocumentPayload,
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

export default {
  list,
  get,
  create,
  update,
  remove,
};
