import api from "./api";
import type { DossierItem, CreateDossierPayload } from "../types/dossier";

async function list(): Promise<DossierItem[]> {
  const response = await api.get<DossierItem[]>("/dossiers");
  return response.data;
}

async function create(payload: CreateDossierPayload): Promise<DossierItem> {
  const response = await api.post<DossierItem>("/dossiers", payload);
  return response.data;
}

async function remove(id: string): Promise<void> {
  await api.delete(`/dossiers/${id}`);
}

export default {
  list,
  create,
  remove,
};
