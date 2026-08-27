export type IaTypeAction = "reformuler" | "corriger" | "completer";
export type IaScope = "selection" | "document";

export interface GenererIaPayload {
  type_action: IaTypeAction;
  scope: IaScope;
  contenu: string;
  instructions?: string;
}

export interface GenererIaResponse {
  id_ia: string;
  content_after: string;
  tokens_used: number;
}

export interface IaHistoriqueEntry {
  id_ia: string;
  type_action: IaTypeAction;
  content_before: string;
  content_after: string;
  tokens_used: number;
  created_at: string;
}
