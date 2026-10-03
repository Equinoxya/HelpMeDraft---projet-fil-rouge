import type { IaTypeAction } from "../types/ia";

/**
 * Estimation du temps de génération de l'IA.
 *
 * POURQUOI UNE ESTIMATION PLUTÔT QU'UN DÉLAI MAXIMUM
 *
 * Le backend n'interrompt plus l'inférence : sur une machine sans carte
 * graphique, une reformulation de quelques milliers de caractères dépasse la
 * minute, et la couper affichait une erreur alors que la génération
 * aboutissait. Reste le vrai problème, qui n'était pas technique : un bouton
 * « Génération en cours… » figé pendant une minute ne dit pas si quelque chose
 * avance ou si l'application est bloquée.
 *
 * D'où ce module : annoncer l'attente au lieu de l'interrompre.
 *
 * COMMENT LE CALCUL EST FAIT
 *
 * La vitesse d'inférence est bornée par la bande passante mémoire : à chaque
 * jeton généré, le processeur relit tous les poids du modèle. Le débit est donc
 * à peu près CONSTANT pour un modèle et une machine donnés, ce qui rend le
 * temps de génération proportionnel au nombre de jetons à produire. C'est ce
 * qui rend l'estimation possible, et aussi ce qui la rend grossière : elle
 * suppose une machine qui ne fait rien d'autre.
 *
 * L'estimation est donc un ORDRE DE GRANDEUR affiché pour situer l'attente,
 * jamais une promesse. L'interface doit rester correcte quand elle est
 * dépassée — voir le compteur dans DocumentEditorView.vue.
 *
 * LIMITE CONNUE : LES MODÈLES À RAISONNEMENT
 *
 * Le calcul suppose que la longueur de la sortie suit celle de l'entrée. Un
 * modèle à raisonnement (qwen3, deepseek-r1) viole cette hypothèse : il
 * produit d'abord un bloc <think>...</think> de taille à peu près CONSTANTE,
 * qui domine tout le reste sur un texte court. Corriger « BJR » demandait
 * ainsi plusieurs minutes là où l'estimation annonçait cinq secondes.
 *
 * C'est pourquoi le backend désactive ce mode (OLLAMA_THINK, false par
 * défaut). Si quelqu'un le réactive, l'estimation redeviendra fausse sur les
 * textes courts — et le compteur basculera simplement sur « plus long que
 * prévu », ce qui reste correct, mais peu informatif.
 */

/**
 * Débit d'inférence de la machine, en jetons par seconde.
 *
 * Valeur par défaut : qwen3:4b sur processeur seul, la configuration la plus
 * lente sur laquelle le projet doit tourner. Une machine avec carte graphique
 * monte à 40 jetons/s et surchargera cette valeur via frontend/.env.
 */
export const JETONS_PAR_SECONDE = Number(
  import.meta.env.VITE_IA_JETONS_PAR_SECONDE ?? 15,
);

/** Environ 3,7 caractères par jeton en français. */
const CARACTERES_PAR_JETON = 3.7;

/**
 * Secondes ajoutées au calcul pour le chargement du modèle, la lecture du
 * prompt et l'aller-retour HTTP. Constant, donc visible surtout sur les
 * textes courts.
 */
const SURCOUT_SECONDES = 4;

/**
 * Longueur de la réponse attendue, en proportion du texte envoyé.
 *
 * Reformuler et corriger réécrivent le texte entier : la sortie fait à peu près
 * la taille de l'entrée. Compléter ne produit qu'une suite, bien plus courte
 * que ce qu'il a reçu — l'estimer comme une réécriture complète annoncerait le
 * double du temps réel.
 */
const RATIO_SORTIE: Record<IaTypeAction, number> = {
  reformuler: 1,
  corriger: 1,
  completer: 0.4,
};

/**
 * Temps de génération estimé, en secondes (toujours au moins 1).
 */
export function estimerDureeGeneration(
  contenu: string,
  typeAction: IaTypeAction,
): number {
  const jetonsASortir =
    (contenu.length / CARACTERES_PAR_JETON) * (RATIO_SORTIE[typeAction] ?? 1);
  const secondes = jetonsASortir / JETONS_PAR_SECONDE + SURCOUT_SECONDES;
  return Math.max(1, Math.round(secondes));
}

/**
 * Durée lisible : « 45 s », « 1 min 25 s ».
 *
 * Les secondes sont conservées au-delà de la minute : pendant une attente, le
 * chiffre qui bouge est le signe que quelque chose avance. « 1 min » figé
 * pendant soixante secondes ressemble à un blocage.
 */
export function formaterDuree(secondes: number): string {
  const total = Math.max(0, Math.round(secondes));
  if (total < 60) return `${total} s`;
  const minutes = Math.floor(total / 60);
  const reste = total % 60;
  return reste === 0 ? `${minutes} min` : `${minutes} min ${reste} s`;
}

/**
 * Avancement entre 0 et 1, pour la barre de progression.
 *
 * Plafonné à 0,95 : une barre qui atteint 100 % alors que la génération
 * continue est pire qu'une barre lente, elle fait croire que l'application est
 * bloquée. Au-delà de l'estimation, l'interface le dit avec un texte.
 */
export function avancementEstime(ecoule: number, estimation: number): number {
  if (estimation <= 0) return 0;
  return Math.min(0.95, Math.max(0, ecoule / estimation));
}
