import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { Camera, Entree, Paquets, Trait, ressort, useRessort, type Courbe } from "../anim";
import { Base, Coffre, Etiquette, Pop, Repere } from "../elements";
import { Scene, charger } from "../Scene";
import { C } from "../theme";

// Scène 4b, « deux centres de données » : deux bâtiments marqués HDS, les applications s'allument dans les deux,
// les bases sont copiées de l'un vers l'autre, puis le coffre de la sauvegarde immuable se ferme.
const S = charger("04b");
const a = S.a;
const T = {
  brique: a("Deuxième brique"),
  centres: a("deux centres de données"),
  certifies: a("certifiés"),
  hds: a("H-D-S"),
  applications: a("Les applications"),
  bases: a("Les bases"),
  copiees: a("copiées"),
  sauvegarde: a("une sauvegarde"),
  immuable: a("immuable"),
  effacer: a("ne peut pas effacer"),
};
export const DUREE_SCENE_4B = S.duree;

const CENTRES = [500, 1420]; // abscisse des deux bâtiments
const Y = 460;
const COPIE: Courbe[] = [[[700, 555], [870, 555], [1050, 555], [1220, 555]]];
const versCoffre = (x: number, sens: number): Courbe[] => [[[x, 650], [x, 760], [960 - sens * 250, 720], [960 - sens * 112, 800]]];

const Batiment: React.FC<{ x: number; retard: number }> = ({ x, retard }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const sigle = ressort(frame, fps, T.hds + retard, 0.5);
  return (
    <>
      <Pop t={T.centres + retard} x={x} y={Y}>
        <rect x={-200} y={-190} width={400} height={380} rx={22} fill={C.panneau} stroke={C.texte} strokeWidth={5} />
        {/* Les applications publiées : trois tuiles qui s'allument */}
        {[-140, -40, 60].map((dx, k) => {
          const allumee = ressort(frame, fps, T.applications + retard + k * 0.12, 0.5);
          return <rect key={dx} x={dx} y={-140} width={80} height={80} rx={14} fill={C.texte} opacity={0.14 + 0.86 * allumee} />;
        })}
      </Pop>
      <Pop t={T.bases + retard} x={x} y={Y + 95}>
        <Base />
      </Pop>
      {/* Le certificat : le cadre arrive à « certifiés », le sigle à « HDS » */}
      <Pop t={T.certifies + retard} x={x + 150} y={Y - 190}>
        <rect x={-80} y={-38} width={160} height={76} rx={38} fill={C.fond} stroke={C.texte} strokeWidth={5} />
        <Etiquette x={0} y={15} taille={42} gras opacity={sigle}>
          HDS
        </Etiquette>
      </Pop>
    </>
  );
};

export const Scene4b: React.FC = () => {
  const ferme = useRessort(T.effacer, undefined, { damping: 13, stiffness: 140 });
  return (
    <Scene de={S}>
      <Camera
        plans={[
          { t: 0, x: 960, y: 540, zoom: 1 },
          { t: T.applications - 0.2, x: 960, y: 460, zoom: 1.12 }, // les deux bâtiments
          { t: T.sauvegarde - 0.2, x: 960, y: 540, zoom: 1 }, // recul : le coffre
        ]}
      >
        <svg viewBox="0 0 1920 1080" style={{ position: "absolute", inset: 0 }}>
          {/* La copie des bases, d'un centre vers l'autre */}
          <Trait d="M 700 555 H 1206" t={T.copiees} duree={0.8} stroke={C.reseau} strokeWidth={6} />
          <Trait d="M 1180 530 L 1210 555 L 1180 580" t={T.copiees + 0.6} duree={0.3} stroke={C.reseau} strokeWidth={6} strokeLinejoin="round" />
          <Paquets route={COPIE} debut={T.copiees + 0.3} fin={T.sauvegarde} periode={0.55} trajet={1.3} couleur="#d9fffd" />
          {/* La sauvegarde part des deux centres vers le coffre */}
          <Trait d={`M ${CENTRES[0]} 650 C ${CENTRES[0]} 760, 710 720, 848 800`} t={T.sauvegarde + 0.2} stroke={C.doux} strokeWidth={4} />
          <Trait d={`M ${CENTRES[1]} 650 C ${CENTRES[1]} 760, 1210 720, 1072 800`} t={T.sauvegarde + 0.35} stroke={C.doux} strokeWidth={4} />
          <Paquets route={versCoffre(CENTRES[0], 1)} debut={T.sauvegarde + 0.6} fin={T.effacer - 0.4} periode={0.7} trajet={1.1} rayon={7} couleur={C.texte} />
          <Paquets route={versCoffre(CENTRES[1], -1)} debut={T.sauvegarde + 0.8} fin={T.effacer - 0.4} periode={0.7} trajet={1.1} rayon={7} couleur={C.texte} />

          <Batiment x={CENTRES[0]} retard={0} />
          <Batiment x={CENTRES[1]} retard={0.25} />
          <Pop t={T.sauvegarde} x={960} y={860}>
            <Coffre ferme={ferme} />
          </Pop>
        </svg>
        <Entree t={T.immuable} style={{ left: 1110, top: 824, fontSize: 56, fontWeight: 700, whiteSpace: "nowrap" }}>
          Sauvegarde immuable
        </Entree>
      </Camera>
      <Repere t={T.brique} numero={2}>
        Deux centres de données
      </Repere>
    </Scene>
  );
};
