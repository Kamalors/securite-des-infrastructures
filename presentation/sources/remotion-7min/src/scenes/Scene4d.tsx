import React from "react";
import { interpolateColors, useCurrentFrame, useVideoConfig } from "remotion";
import { Apparait, Camera, Compteur, Entree, Trait, ressort } from "../anim";
import { Cadenas, Etiquette, Personne, Pop, Repere } from "../elements";
import { Scene, charger } from "../Scene";
import { C } from "../theme";

// Scène 4d, « ceux qui travaillent à distance » : les nomades et les partenaires passent par le second facteur
// et n'atteignent que leur application. À droite, en grisé, le VPN classique : tout le réseau est ouvert,
// avec un poste piraté au milieu.
const S = charger("04d");
const a = S.a;
const T = {
  brique: a("Quatrième brique"),
  nomades: a("Trois mille"),
  partenaires: a("utilisateurs des partenaires"),
  zero: a("Zéro Confiance"),
  ztna: a("Z-T-N-A"),
  identite: a("prouve son identité"),
  facteur: a("second facteur"),
  atteint: a("n'atteint"),
  applications: a("ses applications"),
  jamais: a("jamais le réseau"),
  difference: a("La différence"),
  classique: a("réseau privé virtuel"),
  vpn: a("V-P-N"),
  pirate: a("poste piraté"),
  porte: a("porte d'entrée"),
};
export const DUREE_SCENE_4D = S.duree;

const CADENAS = { x: 700, y: 540 };
const tuile = (origine: number, i: number) => ({ x: origine + (i % 3) * 120, y: 370 + Math.floor(i / 3) * 120 });
const MIENNE = 3; // l'application de l'utilisateur : la tuile du milieu, côté gauche
const PIRATE = 4; // le poste piraté : la tuile du centre

const Schema: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const ouvert = Math.max(0, ressort(frame, fps, T.facteur, undefined, { damping: 11, stiffness: 180 }));
  const rebond = ressort(frame, fps, T.porte, undefined, { damping: 6, stiffness: 200 }) - ressort(frame, fps, T.porte);
  const sombre = ressort(frame, fps, T.jamais, 0.6);
  const allumee = ressort(frame, fps, T.applications, 0.5);
  const pirate = ressort(frame, fps, T.pirate, undefined, { damping: 9 });
  return (
    <svg viewBox="0 0 1920 1080" style={{ position: "absolute", inset: 0 }}>
      {/* Les nomades et les partenaires */}
      {[150, 235, 320].map((x, i) => (
        <Pop key={x} t={T.nomades + i * 0.1} x={x} y={330}>
          <Personne />
        </Pop>
      ))}
      {[150, 235].map((x, i) => (
        <Pop key={x} t={T.partenaires + i * 0.1} x={x} y={640}>
          <Personne couleur={C.doux} />
        </Pop>
      ))}

      {/* Chacun prouve son identité : le cadenas du second facteur s'ouvre */}
      <Trait d={`M 400 350 C 520 350, 540 ${CADENAS.y}, 630 ${CADENAS.y}`} t={T.identite} stroke={C.zt} strokeWidth={5} />
      <Trait d={`M 400 660 C 520 660, 540 ${CADENAS.y}, 630 ${CADENAS.y}`} t={T.identite + 0.15} stroke={C.zt} strokeWidth={5} />
      <Pop t={T.identite + 0.3} x={CADENAS.x} y={CADENAS.y}>
        <g transform={`scale(${1.9 * (1 + 0.25 * rebond)})`}>
          <Cadenas ouvert={ouvert} couleur={C.zt} />
        </g>
      </Pop>
      <Etiquette x={CADENAS.x} y={700} taille={40} couleur={C.zt} opacity={ressort(frame, fps, T.facteur, 0.5)}>
        second facteur
      </Etiquette>

      {/* Zéro Confiance : seule l'application de l'utilisateur s'allume */}
      <Trait d={`M 770 ${CADENAS.y} H 890`} t={T.applications - 0.3} duree={0.5} stroke={C.ok} strokeWidth={6} />
      {Array.from({ length: 9 }, (_, i) => {
        const { x, y } = tuile(900, i);
        const p = ressort(frame, fps, T.atteint + i * 0.04, undefined, { damping: 14 });
        const mienne = i === MIENNE;
        return (
          <rect
            key={i}
            x={x + 50 - 50 * p}
            y={y + 50 - 50 * p}
            width={100 * p}
            height={100 * p}
            rx={16}
            fill={mienne ? interpolateColors(allumee, [0, 1], [C.bord, C.ok]) : C.bord}
            opacity={mienne ? 1 : 1 - 0.55 * sombre}
          />
        );
      })}

      {/* VPN classique : tout le réseau s'allume, et le poste piraté est au milieu */}
      {Array.from({ length: 9 }, (_, i) => {
        const { x, y } = tuile(1420, i);
        const p = ressort(frame, fps, T.classique + 0.3 + i * 0.04, undefined, { damping: 14 });
        const ouverte = ressort(frame, fps, T.vpn + i * 0.06, 0.4);
        const couleur = i === PIRATE ? interpolateColors(pirate, [0, 1], [C.doux, C.refus]) : C.doux;
        const taille = 100 * p * (i === PIRATE ? 1 + 0.12 * Math.max(0, pirate - 1) * 8 : 1);
        return <rect key={i} x={x + 50 - taille / 2} y={y + 50 - taille / 2} width={taille} height={taille} rx={16} fill={couleur} opacity={0.2 + 0.8 * ouverte} />;
      })}
    </svg>
  );
};

export const Scene4d: React.FC = () => (
  <Scene de={S}>
    <Camera
      plans={[
        { t: 0, x: 690, y: 540, zoom: 1.2 }, // le côté Zéro Confiance
        { t: T.difference, x: 960, y: 540, zoom: 1 }, // recul : le VPN classique apparaît à droite
      ]}
    >
      <Schema />
      <Entree t={T.nomades} style={{ left: 100, top: 385, fontSize: 40, color: C.doux, whiteSpace: "nowrap" }}>
        <span style={{ fontSize: 76, fontWeight: 700, color: C.texte, marginRight: 16 }}>
          <Compteur valeur={3000} t={T.nomades} duree={1} />
        </span>
        <br />
        salariés nomades
      </Entree>
      <Entree t={T.partenaires} style={{ left: 100, top: 695, fontSize: 40, color: C.doux, whiteSpace: "nowrap" }}>
        <span style={{ fontSize: 76, fontWeight: 700, color: C.texte }}>≈ 60</span>
        <br />
        organisations partenaires
      </Entree>
      <Entree t={T.zero} style={{ left: 620, top: 200, fontSize: 76, fontWeight: 700, color: C.zt, whiteSpace: "nowrap" }}>
        Zéro Confiance
        <Apparait t={T.ztna} style={{ marginLeft: 28, padding: "4px 26px", borderRadius: 50, border: `3px solid ${C.zt}`, fontSize: 44, verticalAlign: "middle" }}>
          ZTNA
        </Apparait>
      </Entree>
      <Entree t={T.classique} style={{ left: 1420, top: 216, fontSize: 56, fontWeight: 700, color: C.doux, whiteSpace: "nowrap" }}>
        VPN classique
      </Entree>
    </Camera>
    <Repere t={T.brique} numero={4} couleur={C.zt}>
      Travailler à distance
    </Repere>
  </Scene>
);
