import type { DocumentStatus } from "../types/document";

export const statusLabels: Record<DocumentStatus, string> = {
  brouillon: "Brouillon",
  a_relire: "À relire",
  termine: "Terminé",
};

export function getStatusStyle(status: DocumentStatus): string {
  switch (status) {
    case "brouillon":
      return "bg-[#111111] text-[#F4F1EA]";
    case "a_relire":
      return "bg-[#E0533C] text-[#F4F1EA]";
    case "termine":
      return "bg-[#F4F1EA] text-[#111111] border border-[#111111]";
  }
}
