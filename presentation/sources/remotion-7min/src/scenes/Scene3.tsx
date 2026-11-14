import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { Camera, ressort, useRessort } from "../anim";
import { Baie, Immeuble, Pop } from "../elements";
import { Scene, charger } from "../Scene";
import { C } from "../theme";

// Scène 3, ce que le client va noter : trois cartes se retournent l'une après l'autre, puis un tampon sur la troisième.
const S = charger("03");
const a = S.a;
const T = {
  cartes: a("trois critères"),
  un: a("Un pour chaque"),
  equipement: a("l'équipement retenu"),
  deux: a("Deux les schémas"),
  centre: a("pour le centre"),
  agences: a("pour les agences"),
  trois: a("Trois le coût"),
  poste: a("poste par poste"),
  preference: a("préférence nette"),
};
export const DUREE_SCENE_3 = S.duree;

const LARGEUR = 500;
const gauche = (i: number) => 180 + i * 530;
const face: React.CSSProperties = {
  position: "absolute",
  inset: 0,
  boxSizing: "border-box",
  borderRadius: 32,
  background: C.panneau,
  backfaceVisibility: "hidden",
};

/** Carte posée face cachée, qui se retourne à l'instant `t`. */
const Carte: React.FC<{ i: number; t: number; titre: React.ReactNode; children: React.ReactNode }> = ({ i, t, titre, children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pose = ressort(frame, fps, T.cartes + i * 0.12, undefined, { damping: 14 });
  const retournee = ressort(frame, fps, t, 0.9);
  return (
    <div style={{ position: "absolute", left: gauche(i), top: 250, width: LARGEUR, height: 560, perspective: 1800, scale: pose, opacity: Math.min(1, pose * 3) }}>
      <div style={{ position: "absolute", inset: 0, transformStyle: "preserve-3d", rotate: `y ${180 * (1 - retournee)}deg` }}>
        <div style={{ ...face, border: `4px solid ${C.texte}`, padding: "30px 44px" }}>
          <div style={{ fontSize: 120, fontWeight: 700, lineHeight: 1.1, color: C.doux }}>{i + 1}</div>
          <div style={{ fontSize: 52, fontWeight: 700, lineHeight: 1.2, marginTop: 10 }}>{titre}</div>
          <svg viewBox="0 0 412 190" style={{ position: "absolute", left: 44, bottom: 30, width: 412, height: 190 }}>
            {children}
          </svg>
        </div>
        <div style={{ ...face, border: `4px dashed ${C.bord}`, rotate: "y 180deg", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 220, fontWeight: 700, color: C.bord }}>
          ?
        </div>
      </div>
    </div>
  );
};

/** Trois barres qui montent : le coût, poste par poste. */
const Postes: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <>
      {[70, 120, 95].map((hauteur, k) => {
        const p = ressort(frame, fps, T.poste + k * 0.15, undefined, { damping: 14 });
        return <rect key={k} x={10 + k * 70} y={180 - hauteur * p} width={50} height={hauteur * p} rx={8} fill={C.doux} />;
      })}
    </>
  );
};

const Tampon: React.FC = () => {
  const p = useRessort(T.preference, undefined, { damping: 13, stiffness: 160 });
  return (
    <div
      style={{
        position: "absolute",
        left: gauche(2) + 120, // sur le coin haut droit de la carte, sans cacher ni le titre ni les barres
        top: 268,
        padding: "10px 26px",
        border: `6px solid ${C.texte}`,
        borderRadius: 14,
        fontSize: 40,
        fontWeight: 700,
        lineHeight: 1.2,
        letterSpacing: 2,
        textAlign: "center",
        textTransform: "uppercase",
        background: C.panneau,
        rotate: "7deg",
        scale: 1 + 1.6 * (1 - p),
        opacity: Math.min(1, p * 2.5),
      }}
    >
      abonnement
      <br />
      de préférence
    </div>
  );
};

export const Scene3: React.FC = () => (
  <Scene de={S}>
    <Camera
      plans={[
        { t: 0, x: 960, y: 540, zoom: 1 },
        // Glissement léger vers la carte dont parle la voix : les trois cartes restent entières dans le cadre.
        { t: T.un - 0.2, x: 890, y: 540, zoom: 1.06 },
        { t: T.deux - 0.2, x: 960, y: 540, zoom: 1.06 },
        { t: T.trois - 0.2, x: 1030, y: 540, zoom: 1.06 },
      ]}
    >
      <Carte i={0} t={T.un} titre="Les équipements">
        <Pop t={T.equipement} x={130} y={120}>
          <rect x={-120} y={-44} width={240} height={88} rx={14} fill={C.panneau} stroke={C.texte} strokeWidth={5} />
          {[-78, -42, -6, 30].map((x) => (
            <rect key={x} x={x} y={-12} width={24} height={24} rx={5} fill={C.doux} />
          ))}
          <circle cx={88} cy={0} r={9} fill={C.reseau} />
        </Pop>
      </Carte>
      <Carte
        i={1}
        t={T.deux}
        titre={
          <>
            Les schémas
            <br />
            d'architecture
          </>
        }
      >
        <Pop t={T.centre} x={90} y={105}>
          <g transform="scale(0.8)">
            <Baie />
          </g>
        </Pop>
        <Pop t={T.agences} x={290} y={105}>
          <g transform="scale(0.95)">
            <Immeuble />
          </g>
        </Pop>
      </Carte>
      <Carte i={2} t={T.trois} titre="Le coût par poste">
        <Postes />
      </Carte>
      <Tampon />
    </Camera>
  </Scene>
);
