import React from "react";
import { Entree, useRessort } from "./anim";
import { C } from "./theme";

// Éléments de schéma partagés par les scènes. Les pictogrammes sont centrés sur (0, 0) : on les place avec <Pop> ou <g transform>.

/** Texte d'un schéma SVG. */
export const Etiquette: React.FC<{
  x: number;
  y: number;
  taille?: number;
  gras?: boolean;
  couleur?: string;
  ancre?: "start" | "middle" | "end";
  opacity?: number;
  children: React.ReactNode;
}> = ({ x, y, taille = 38, gras, couleur = C.texte, ancre = "middle", opacity, children }) => (
  <text x={x} y={y} textAnchor={ancre} fontSize={taille} fontWeight={gras ? 700 : 400} fill={couleur} opacity={opacity}>
    {children}
  </text>
);

/** Groupe SVG qui surgit à l'instant `t` en grossissant depuis (x, y), et qui se retire à l'instant `fin`. */
export const Pop: React.FC<{ t: number; x: number; y: number; fin?: number; children: React.ReactNode }> = ({
  t,
  x,
  y,
  fin,
  children,
}) => {
  const p = useRessort(t, undefined, { damping: 14 }) * (1 - useRessort(fin ?? 1e6, 0.4));
  return (
    <g opacity={Math.min(1, p * 3)} transform={`translate(${x} ${y}) scale(${p})`}>
      {children}
    </g>
  );
};

/** Croix rouge qui surgit à l'instant `t` : un refus. */
export const Croix: React.FC<{ t: number; x: number; y: number; taille?: number }> = ({ t, x, y, taille = 26 }) => {
  const p = useRessort(t, undefined, { damping: 10 });
  return (
    <g transform={`translate(${x} ${y}) scale(${p}) rotate(45)`} stroke={C.refus} strokeWidth={taille * 0.4} strokeLinecap="round">
      <line x1={-taille} y1={0} x2={taille} y2={0} />
      <line x1={0} y1={-taille} x2={0} y2={taille} />
    </g>
  );
};

/** Coche qui se dessine à l'instant `t`. */
export const Coche: React.FC<{ t: number; x: number; y: number; taille?: number; couleur?: string }> = ({
  t,
  x,
  y,
  taille = 16,
  couleur = C.ok,
}) => {
  const p = useRessort(t, 0.35);
  return (
    <path
      d={`M ${x - taille} ${y} l ${taille * 0.7} ${taille * 0.7} l ${taille * 1.3} ${-taille * 1.4}`}
      fill="none"
      stroke={couleur}
      strokeWidth={taille * 0.45}
      strokeLinecap="round"
      strokeLinejoin="round"
      pathLength={1}
      strokeDasharray={1}
      strokeDashoffset={1 - p}
      opacity={p > 0.001 ? 1 : 0}
    />
  );
};

/** Repère fixe en haut à gauche : la brique en cours. */
export const Repere: React.FC<{ t: number; numero: number; couleur?: string; children: React.ReactNode }> = ({
  t,
  numero,
  couleur = C.reseau,
  children,
}) => (
  <Entree
    t={t}
    dy={-30}
    style={{
      left: 80,
      top: 64,
      display: "flex",
      alignItems: "center",
      gap: 20,
      padding: "12px 30px 12px 14px",
      borderRadius: 50,
      background: C.panneau,
      border: `3px solid ${couleur}`,
      fontSize: 40,
      fontWeight: 700,
      whiteSpace: "nowrap",
    }}
  >
    <span
      style={{
        width: 56,
        height: 56,
        borderRadius: 28,
        background: couleur,
        color: C.fond,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      {numero}
    </span>
    {children}
  </Entree>
);

const trait = { fill: C.panneau, stroke: C.texte, strokeWidth: 4 };

/** Baie de serveurs : un centre de données, ou un serveur. */
export const Baie: React.FC<{ couleur?: string }> = ({ couleur = C.texte }) => (
  <>
    {[-76, -22, 32].map((dy) => (
      <g key={dy}>
        <rect x={-100} y={dy} width={200} height={44} rx={8} {...trait} stroke={couleur} />
        <circle cx={70} cy={dy + 22} r={6} fill={C.reseau} />
      </g>
    ))}
  </>
);

/** Immeuble : un site. */
export const Immeuble: React.FC = () => (
  <>
    <rect x={-60} y={-70} width={120} height={140} rx={10} {...trait} />
    {[0, 1, 2].map((ligne) =>
      [0, 1].map((colonne) => (
        <rect key={`${ligne}-${colonne}`} x={-38 + colonne * 46} y={-52 + ligne * 38} width={30} height={22} rx={4} fill={C.doux} />
      )),
    )}
  </>
);

/** Silhouette : une personne. */
export const Personne: React.FC<{ couleur?: string }> = ({ couleur = C.texte }) => (
  <g fill={couleur}>
    <circle cx={0} cy={-22} r={17} />
    <path d="M -30 36 a 30 30 0 0 1 60 0 z" />
  </g>
);

/** Cadenas. `ouvert` va de 0 (fermé) à 1 (ouvert). */
export const Cadenas: React.FC<{ ouvert?: number; couleur?: string }> = ({ ouvert = 0, couleur = C.texte }) => (
  <g stroke={couleur} strokeWidth={8} fill="none" strokeLinecap="round">
    <path d="M -22 -4 V -30 A 22 22 0 0 1 22 -30 V -4" transform={`translate(0 ${-18 * ouvert}) rotate(${-30 * ouvert} -22 -4)`} />
    <rect x={-40} y={-4} width={80} height={62} rx={12} fill={C.panneau} />
    <circle cx={0} cy={27} r={7} fill={couleur} stroke="none" />
  </g>
);

/** Nuage : Internet. */
export const Nuage: React.FC = () => (
  <path d="M -85 40 a 42 42 0 0 1 4 -84 a 58 58 0 0 1 108 -14 a 50 50 0 0 1 48 98 z" {...trait} strokeLinejoin="round" />
);

/** Cylindre : une base de données. */
export const Base: React.FC<{ couleur?: string }> = ({ couleur = C.texte }) => (
  <g fill={C.panneau} stroke={couleur} strokeWidth={4}>
    <path d="M -44 -34 v 68 a 44 16 0 0 0 88 0 v -68" />
    <ellipse cx={0} cy={-34} rx={44} ry={16} />
    <path d="M -44 0 a 44 16 0 0 0 88 0" fill="none" />
  </g>
);

/** Coffre-fort. `ferme` va de 0 (porte ouverte) à 1 (porte fermée). */
export const Coffre: React.FC<{ ferme?: number }> = ({ ferme = 1 }) => (
  <g stroke={C.texte} strokeWidth={5} strokeLinejoin="round">
    <rect x={-110} y={-95} width={220} height={190} rx={16} fill={C.panneau} />
    <rect x={-86} y={-72} width={172} height={144} rx={10} fill={C.fond} />
    <g transform={`translate(-86 0) scale(${0.25 + 0.75 * ferme} 1) translate(86 0)`}>
      <rect x={-86} y={-72} width={172} height={144} rx={10} fill={C.panneau} />
      <g transform={`rotate(${200 * ferme})`}>
        <circle r={30} fill="none" />
        <path d="M -30 0 H 30 M 0 -30 V 30" />
      </g>
    </g>
  </g>
);
