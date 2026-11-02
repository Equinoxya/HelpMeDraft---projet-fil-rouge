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
  /**
   * Traçabilité AI Act (art. 50). `insere` distingue une proposition versée au
   * document d'une proposition rejetée : les deux produisent une ligne en base,
   * mais une seule constitue un contenu généré présent dans le document.
   *
   * `position_debut` n'est PAS maintenue après l'insertion — elle deviendrait
   * fausse à la première frappe en amont. Elle ne sert qu'à départager deux
   * passages identiques dans un même document.
   */
  insere: boolean;
  position_debut: number | null;
  insere_at: string | null;
}

export interface MarquerInsertionResponse {
  id_ia: string;
  insere: boolean;
  position_debut: number | null;
  insere_at: string | null;
}
