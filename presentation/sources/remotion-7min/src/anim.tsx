import React from "react";
import { spring, useCurrentFrame, useVideoConfig, type SpringConfig } from "remotion";

// Tous les mouvements passent par spring() : aucun déplacement linéaire.
const DOUX: Partial<SpringConfig> = { damping: 200 };

/** Progression 0 → 1 d'un ressort qui démarre à `t` secondes. `duree` l'étire sur un nombre de secondes donné. */
export const ressort = (frame: number, fps: number, t: number, duree?: number, config = DOUX) =>
  spring({
    frame: frame - Math.round(t * fps),
    fps,
    config,
    durationInFrames: duree === undefined ? undefined : Math.round(duree * fps),
  });

export const useRessort = (t: number, duree?: number, config = DOUX) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return ressort(frame, fps, t, duree, config);
};

/** Apparition : fondu et léger glissement, à l'instant `t`. `fin` fait disparaître l'élément de la même façon. */
export const Entree: React.FC<{
  t: number;
  fin?: number;
  dy?: number;
  style?: React.CSSProperties;
  children: React.ReactNode;
}> = ({ t, fin, dy = 36, style, children }) => {
  const p = useRessort(t) - useRessort(fin ?? 1e6);
  return (
    <div style={{ position: "absolute", ...style, opacity: p, translate: `0px ${(1 - p) * dy}px` }}>{children}</div>
  );
};

/** Texte qui apparaît en fondu à l'instant `t`, sans bouger : pour compléter une phrase déjà à l'écran. */
export const Apparait: React.FC<{ t: number; style?: React.CSSProperties; children: React.ReactNode }> = ({ t, style, children }) => (
  <span style={{ ...style, opacity: useRessort(t, 0.5) }}>{children}</span>
);

/** Trait SVG qui se dessine à l'instant `t`. À placer dans un <svg>. */
export const Trait: React.FC<{ d: string; t: number; duree?: number; opacity?: number } & React.SVGProps<SVGPathElement>> = ({
  d,
  t,
  duree = 0.9,
  opacity = 1,
  ...reste
}) => {
  const p = useRessort(t, duree);
  return (
    <path
      d={d}
      fill="none"
      strokeLinecap="round"
      pathLength={1}
      strokeDasharray={1}
      strokeDashoffset={1 - p}
      opacity={p > 0.001 ? opacity : 0} // invisible avant de commencer : sinon l'extrémité arrondie laisse un point
      {...reste}
    />
  );
};

/** Nombre qui défile de 0 à `valeur` à partir de l'instant `t`, écrit à la française. */
export const Compteur: React.FC<{ valeur: number; t: number; duree?: number; decimales?: number }> = ({
  valeur,
  t,
  duree = 1.4,
  decimales = 0,
}) => {
  const p = useRessort(t, duree);
  const texte = (valeur * p)
    .toLocaleString("fr-FR", { minimumFractionDigits: decimales, maximumFractionDigits: decimales })
    .replace(/\u202f/g, "\u00a0"); // espace insécable simple : présente dans toutes les polices
  return <span style={{ fontVariantNumeric: "tabular-nums" }}>{texte}</span>;
};

export type Plan = { t: number; x: number; y: number; zoom: number };

/**
 * Caméra : cadre le point (x, y) du plan de travail 1920 × 1080 avec un zoom.
 * À chaque instant `t` d'un plan, elle rejoint ce cadrage par un ressort.
 */
export const Camera: React.FC<{ plans: Plan[]; children: React.ReactNode }> = ({ plans, children }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  let { x, y, zoom } = plans[0];
  for (const plan of plans.slice(1)) {
    const p = ressort(frame, fps, plan.t, 1.2);
    x += (plan.x - x) * p;
    y += (plan.y - y) * p;
    zoom += (plan.zoom - zoom) * p;
  }
  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        scale: zoom,
        translate: `${(width / 2 - x) * zoom}px ${(height / 2 - y) * zoom}px`,
      }}
    >
      {children}
    </div>
  );
};

export type Pt = [number, number];
export type Courbe = [Pt, Pt, Pt, Pt]; // Bézier cubique

/** Tracé SVG d'une route : une ou plusieurs courbes mises bout à bout. */
export const chemin = (route: Courbe[]) =>
  `M ${route[0][0].join(" ")} ` + route.map(([, b, c, d]) => `C ${b.join(" ")}, ${c.join(" ")}, ${d.join(" ")}`).join(" ");

/** Point d'une route à la progression `t` (0 à 1), chaque courbe comptant pour une part égale. */
export const pointSur = (route: Courbe[], t: number): Pt => {
  const i = Math.min(route.length - 1, Math.floor(t * route.length));
  const [a, b, c, d] = route[i];
  const v = t * route.length - i;
  const u = 1 - v;
  const en = (k: 0 | 1) => u * u * u * a[k] + 3 * u * u * v * b[k] + 3 * u * v * v * c[k] + v * v * v * d[k];
  return [en(0), en(1)];
};

/** Paquets qui parcourent une route entre `debut` et `fin` (secondes), un toutes les `periode` secondes. À placer dans un <svg>. */
export const Paquets: React.FC<{
  route: Courbe[];
  debut: number;
  fin: number;
  couleur: string;
  periode?: number;
  trajet?: number;
  rayon?: number;
}> = ({ route, debut, fin, couleur, periode = 0.7, trajet = 1.6, rayon = 9 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const paquets = [];
  for (let depart = debut; depart < fin; depart += periode) {
    const p = ressort(frame, fps, depart, trajet);
    if (p <= 0 || p >= 0.999) continue;
    const [x, y] = pointSur(route, p);
    paquets.push(<circle key={depart} cx={x} cy={y} r={rayon} fill={couleur} opacity={Math.min(1, p * 8, (1 - p) * 8)} />);
  }
  return <>{paquets}</>;
};
