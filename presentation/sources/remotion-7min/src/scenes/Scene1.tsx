import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { Camera, Compteur, Entree, Paquets, Trait, ressort, useRessort, type Courbe, type Pt } from "../anim";
import carte from "../donnees/carte.json";
import { Scene, Son, charger } from "../Scene";
import { C } from "../theme";

// Scène 1, l'accroche : 530 points s'allument, des traits les relient à deux centres, puis le titre.
// Chaque instant vient de la voix : l'élément apparaît quand le mot est prononcé.
const S = charger("01");
const a = S.a;
const T = {
  sites: a("cinq cent trente"),
  utilisateurs: a("dix mille"),
  sante: a("données de santé"),
  reseau: a("sans faire exploser"),
  question: a("C'est la question"),
  titre: a("Voici notre réponse"),
};
export const DUREE_SCENE_1 = S.duree;

const POINTS = carte.points as Pt[]; // dans l'ordre d'allumage
const CENTRES: Pt[] = [
  [880, 300],
  [880, 520],
];
const TERRE = "#151f35";

const Points: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <>
      {POINTS.map(([x, y], i) => {
        const p = ressort(frame, fps, T.sites + (i / POINTS.length) * 1.5, undefined, { damping: 14 });
        return p > 0.001 ? <circle key={i} cx={x} cy={y} r={3.6 * p} fill={C.reseau} /> : null;
      })}
    </>
  );
};

// Chaque site est relié aux deux centres. Les traits partent par lots, pour ne pas tous bouger en même temps.
const LOTS = 12;
const Liaisons: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const lots = [];
  for (let lot = 0; lot < LOTS; lot++) {
    const p = ressort(frame, fps, T.reseau + 0.5 + lot * 0.09, 1.1);
    if (p <= 0.001) continue;
    let d = "";
    for (let i = lot; i < POINTS.length; i += LOTS) {
      const [x, y] = POINTS[i];
      for (const [cx, cy] of CENTRES) {
        d += `M${x} ${y}L${(x + (cx - x) * p).toFixed(1)} ${(y + (cy - y) * p).toFixed(1)}`;
      }
    }
    lots.push(<path key={lot} d={d} stroke={C.reseau} strokeWidth={1} opacity={0.13} fill="none" />);
  }
  return <>{lots}</>;
};

const Centre: React.FC<{ centre: Pt }> = ({ centre: [x, y] }) => {
  const p = useRessort(T.reseau, undefined, { damping: 12 });
  return (
    <rect x={x - 32 * p} y={y - 32 * p} width={64 * p} height={64 * p} rx={14 * p} fill={C.panneau} stroke={C.reseau} strokeWidth={5} />
  );
};

// Quelques paquets voyagent vers les centres pendant que la voix pose la question.
const droite = ([x1, y1]: Pt, [x2, y2]: Pt): Courbe[] => [[
  [x1, y1],
  [x1 + (x2 - x1) / 3, y1 + (y2 - y1) / 3],
  [x1 + ((x2 - x1) * 2) / 3, y1 + ((y2 - y1) * 2) / 3],
  [x2, y2],
]];
const TRAJETS = Array.from({ length: 14 }, (_, k) => droite(POINTS[k * 37], CENTRES[k % 2]));

const Statistique: React.FC<{ t: number; top: number; children: React.ReactNode }> = ({ t, top, children }) => (
  <Entree t={t} fin={T.titre - 0.4} style={{ left: 1060, top, fontSize: 60, color: C.doux, whiteSpace: "nowrap" }}>
    {children}
  </Entree>
);
const Chiffre: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <span style={{ fontSize: 104, fontWeight: 700, color: C.texte, marginRight: 24 }}>{children}</span>
);

export const Scene1: React.FC = () => {
  const carteVisible = useRessort(0.2);
  return (
    <Scene de={S}>
      <Camera
        plans={[
          { t: 0, x: 960, y: 540, zoom: 1 },
          { t: 0.2, x: 720, y: 540, zoom: 1.12 }, // la France, pendant que les sites s'allument
          { t: T.reseau, x: 960, y: 540, zoom: 1 }, // recul : le monde et les deux centres
        ]}
      >
        <svg viewBox="0 0 1920 1080" style={{ position: "absolute", inset: 0 }}>
          <path d={carte.monde} fill={TERRE} stroke={C.bord} strokeWidth={1} opacity={carteVisible} />
          <path d={carte.france} fill={TERRE} opacity={carteVisible} />
          <Trait d={carte.france} t={0.2} duree={1.4} stroke={C.reseau} strokeWidth={2.5} />
          <Liaisons />
          <Points />
          {TRAJETS.map((trajet, k) => (
            <Paquets key={k} route={trajet} debut={T.question + k * 0.12} fin={T.titre - 0.5} periode={1.2} trajet={1.1} rayon={5} couleur={C.texte} />
          ))}
          {CENTRES.map((centre, i) => (
            <Centre key={i} centre={centre} />
          ))}
        </svg>
      </Camera>

      <Statistique t={T.sites} top={580}>
        <Chiffre>
          <Compteur valeur={530} t={T.sites} duree={1} />
        </Chiffre>
        sites
      </Statistique>
      <Statistique t={T.utilisateurs} top={705}>
        <Chiffre>
          <Compteur valeur={10000} t={T.utilisateurs} duree={1} />
        </Chiffre>
        utilisateurs
      </Statistique>
      <Statistique t={T.sante} top={850}>
        <span style={{ fontSize: 72, fontWeight: 700, color: C.texte }}>Données de santé</span>
      </Statistique>
      <Son t={T.sites} fichier="compteur.wav" />
      <Son t={T.utilisateurs} fichier="compteur.wav" />

      <Entree t={T.titre} style={{ left: 1060, top: 620, fontSize: 100, fontWeight: 700, lineHeight: 1.15, whiteSpace: "nowrap" }}>
        Le projet RAO
        <br />
        en 5 minutes
      </Entree>
    </Scene>
  );
};
