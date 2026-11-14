// Calage au mot : les animations démarrent à l'instant où la voix prononce une expression.

export type Mot = { mot: string; debut: number; fin: number };
export type Voix = { duree: number; mots: Mot[] };
type Fichier = Voix & { parties: Record<string, { debut: number; duree: number }> };

const normaliser = (s: string) =>
  s
    .toLowerCase()
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/[^a-z0-9]+/g, " ")
    .trim();

/**
 * Seconde où la voix commence à prononcer `expression` (sa n-ième occurrence).
 * Lève une erreur si l'expression est absente : un calage faux ne doit pas passer en silence.
 */
export const instant = (voix: Voix, expression: string, occurrence = 1): number => {
  const jetons = voix.mots.flatMap((m) =>
    normaliser(m.mot)
      .split(" ")
      .filter(Boolean)
      .map((j) => ({ j, debut: m.debut })),
  );
  const cible = normaliser(expression).split(" ");
  let vu = 0;
  for (let i = 0; i + cible.length <= jetons.length; i++) {
    if (cible.every((c, k) => jetons[i + k].j === c) && ++vu === occurrence) {
      return jetons[i].debut;
    }
  }
  throw new Error(`Calage : « ${expression} » (occurrence ${occurrence}) introuvable dans la voix`);
};

/** Une partie d'un fichier de voix (par exemple « 04a »), avec un minutage qui repart de zéro. `debut` situe la partie dans le fichier. */
export const partie = (fichier: Fichier, cle: string): Voix & { debut: number } => {
  const { debut, duree } = fichier.parties[cle];
  return {
    debut,
    duree,
    mots: fichier.mots
      .filter((m) => m.debut >= debut && m.debut < debut + duree)
      .map((m) => ({ mot: m.mot, debut: m.debut - debut, fin: m.fin - debut })),
  };
};
