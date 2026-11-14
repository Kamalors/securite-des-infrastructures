import React from "react";
import { interpolateColors, useCurrentFrame, useVideoConfig } from "remotion";
import { Camera, Compteur, Entree, Paquets, Trait, chemin, ressort, useRessort, type Courbe } from "../anim";
import { Repere } from "../elements";
import { Scene, Son, charger } from "../Scene";
import { C } from "../theme";

// Scène 4a, « relier les sites » : un site, son FortiGate, deux opérateurs, des tunnels vers les deux centres
// de données, puis la coupure de la ligne A et la bascule sur la ligne B.
const S = charger("04a");
const a = S.a;
const T = {
  solution: a("Notre solution"),
  briques: a("quatre briques"),
  premiere: a("Première brique"),
  relier: a("relier les sites"),
  site: a("Chaque site"),
  fortigate: a("pare-feu FortiGate"),
  acces: a("deux accès"),
  tunnels: a("tunnels chiffrés"),
  centres: a("vers les deux centres"),
  sdwan: a("S-D-WAN"),
  pilote: a("un réseau étendu"),
  meilleur: a("le meilleur chemin"),
  etSi: a("Et si un opérateur"),
  tombe: a("tombe"),
  bascule: a("Le trafic bascule"),
  autre: a("sur l'autre"),
  moins: a("en moins de quatre secondes"),
};
export const DUREE_SCENE_4A = S.duree;

// Géométrie du schéma, dans l'image 1920 × 1080.
const HAUT = 340; // ligne de l'opérateur A et du centre de données 1
const BAS = 780; // ligne de l'opérateur B et du centre de données 2
const acces = (y: number): Courbe => [[680, 560], [770, 560], [750, y], [840, y]];
const traversee = (y: number): Courbe => [[840, y], [933, y], [1027, y], [1120, y]];
const versCentre = (y1: number, y2: number): Courbe => [[1120, y1], [1320, y1], [1280, y2], [1480, y2]];
const route = (operateur: number, centre: number): Courbe[] => [acces(operateur), traversee(operateur), versCentre(operateur, centre)];
const COUPURE = { x: 760, y: 450 }; // milieu de la ligne d'accès A
const PAQUET = "#d9fffd";

const Etiquette: React.FC<{ x: number; y: number; taille?: number; gras?: boolean; children: React.ReactNode }> = ({
  x,
  y,
  taille = 38,
  gras,
  children,
}) => (
  <text x={x} y={y} textAnchor="middle" fontSize={taille} fontWeight={gras ? 700 : 400} fill={C.texte}>
    {children}
  </text>
);

/** Groupe SVG qui apparaît à l'instant `t` en grossissant depuis son centre. */
const Pop: React.FC<{ t: number; x: number; y: number; children: React.ReactNode }> = ({ t, x, y, children }) => {
  const p = useRessort(t, undefined, { damping: 14 });
  return (
    <g opacity={Math.min(1, p * 3)} transform={`translate(${x} ${y}) scale(${p}) translate(${-x} ${-y})`}>
      {children}
    </g>
  );
};

const CentreDeDonnees: React.FC<{ y: number; numero: number }> = ({ y, numero }) => (
  <Pop t={T.centres + (numero - 1) * 0.2} x={1580} y={y}>
    {[-76, -22, 32].map((dy) => (
      <g key={dy}>
        <rect x={1480} y={y + dy} width={200} height={44} rx={8} fill={C.panneau} stroke={C.texte} strokeWidth={4} />
        <circle cx={1650} cy={y + dy + 22} r={6} fill={C.reseau} />
      </g>
    ))}
    <Etiquette x={1580} y={y + 130} taille={36}>
      Centre de données {numero}
    </Etiquette>
  </Pop>
);

const Schema: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const coupe = ressort(frame, fps, T.tombe, 0.5); // la ligne A tombe
  const croix = ressort(frame, fps, T.tombe, undefined, { damping: 10 });
  const meilleur = ressort(frame, fps, T.meilleur, 0.6) - ressort(frame, fps, T.etSi, 0.6); // le chemin par A est mis en avant
  const couleurA = interpolateColors(coupe, [0, 1], [C.reseau, C.refus]);
  const finA = T.tombe - 0.15; // plus aucun paquet ne part par A une fois la ligne coupée

  return (
    <svg viewBox="0 0 1920 1080" style={{ position: "absolute", inset: 0 }}>
      {/* Tunnels chiffrés : un tube translucide et un trait au centre, par chaque opérateur vers chaque centre */}
      {[HAUT, BAS].map((operateur, i) =>
        [HAUT, BAS].map((centre) => {
          const d = chemin(route(operateur, centre));
          const parA = operateur === HAUT;
          const t = T.tunnels + i * 0.35;
          return (
            <g key={`${operateur}-${centre}`} opacity={parA ? 1 - 0.5 * coupe : 1}>
              <Trait d={d} t={t} duree={1.3} stroke={parA ? couleurA : C.reseau} strokeWidth={18} opacity={0.2 + (parA ? 0.25 * meilleur : 0)} />
              <Trait d={d} t={t} duree={1.3} stroke={parA ? couleurA : C.reseau} strokeWidth={3} />
            </g>
          );
        }),
      )}
      {/* Les deux accès à Internet */}
      <Trait d={chemin([acces(HAUT)])} t={T.acces + 0.35} stroke={couleurA} strokeWidth={5} />
      <Trait d={chemin([acces(BAS)])} t={T.acces + 0.6} stroke={C.reseau} strokeWidth={5} />

      {/* Paquets : par l'opérateur A d'abord, puis par B après la coupure */}
      {[HAUT, BAS].map((centre, i) => (
        <React.Fragment key={centre}>
          <Paquets route={route(HAUT, centre)} debut={T.centres + 0.9 + i * 0.3} fin={finA} periode={0.6} trajet={2} couleur={PAQUET} />
          <Paquets route={route(BAS, centre)} debut={T.autre + i * 0.3} fin={DUREE_SCENE_4A} periode={0.6} trajet={2} couleur={PAQUET} />
        </React.Fragment>
      ))}

      {/* Coupure de la ligne A : un trou dans le trait et une croix rouge */}
      <circle cx={COUPURE.x} cy={COUPURE.y} r={30 * coupe} fill="#121c31" />
      <g transform={`translate(${COUPURE.x} ${COUPURE.y}) scale(${croix}) rotate(45)`} stroke={C.refus} strokeWidth={10} strokeLinecap="round">
        <line x1={-26} y1={0} x2={26} y2={0} />
        <line x1={0} y1={-26} x2={0} y2={26} />
      </g>

      {/* Le site et son boîtier */}
      <Pop t={T.site} x={300} y={550}>
        <rect x={240} y={480} width={120} height={140} rx={10} fill={C.panneau} stroke={C.texte} strokeWidth={4} />
        {[0, 1, 2].map((ligne) =>
          [0, 1].map((colonne) => (
            <rect key={`${ligne}-${colonne}`} x={262 + colonne * 46} y={498 + ligne * 38} width={30} height={22} rx={4} fill={C.doux} />
          )),
        )}
        <Etiquette x={300} y={676} taille={40}>
          Site
        </Etiquette>
      </Pop>
      <Trait d="M 360 560 L 440 560" t={T.fortigate} duree={0.4} stroke={C.reseau} strokeWidth={5} />
      <Pop t={T.fortigate} x={560} y={560}>
        <rect x={440} y={518} width={240} height={84} rx={14} fill={C.panneau} stroke={C.reseau} strokeWidth={5} />
        <Etiquette x={560} y={574} gras>
          FortiGate
        </Etiquette>
      </Pop>

      {/* Les deux opérateurs */}
      {[HAUT, BAS].map((y, i) => (
        <Pop key={y} t={T.acces + i * 0.25} x={980} y={y}>
          <rect x={840} y={y - 45} width={280} height={90} rx={45} fill={C.panneau} stroke={i === 0 ? couleurA : C.reseau} strokeWidth={5} />
          <Etiquette x={980} y={y + 13}>Opérateur {i === 0 ? "A" : "B"}</Etiquette>
        </Pop>
      ))}

      <CentreDeDonnees y={HAUT} numero={1} />
      <CentreDeDonnees y={BAS} numero={2} />
    </svg>
  );
};

const NUMEROS = [1, 2, 3, 4];

/** Les quatre briques, puis la première mise en avant. */
const Briques: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const premiere = ressort(frame, fps, T.premiere);
  const sortie = ressort(frame, fps, T.site - 0.25, 0.5);
  return (
    <div style={{ position: "absolute", inset: 0, opacity: 1 - sortie, translate: `0px ${-40 * sortie}px` }}>
      <Entree t={T.solution} style={{ left: 180, top: 230, fontSize: 96, fontWeight: 700 }}>
        Notre solution
      </Entree>
      {NUMEROS.map((numero, i) => {
        const p = ressort(frame, fps, T.briques + i * 0.12, undefined, { damping: 13 });
        const active = i === 0 ? premiere : 0;
        return (
          <div
            key={numero}
            style={{
              position: "absolute",
              left: 180 + i * 400,
              top: 400,
              width: 360,
              height: 250,
              borderRadius: 28,
              boxSizing: "border-box",
              border: `5px solid ${interpolateColors(active, [0, 1], [C.bord, C.reseau])}`,
              background: C.panneau,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 150,
              fontWeight: 700,
              color: interpolateColors(active, [0, 1], [C.texte, C.reseau]),
              scale: p * (1 + 0.06 * active),
              opacity: Math.min(1, p * 3) * (i === 0 ? 1 : 1 - 0.65 * premiere),
            }}
          >
            {numero}
          </div>
        );
      })}
      <Entree t={T.relier} style={{ left: 180, top: 690, fontSize: 68, fontWeight: 700, whiteSpace: "nowrap" }}>
        Relier les sites
      </Entree>
    </div>
  );
};

export const Scene4a: React.FC = () => (
  <Scene de={S}>
    <Camera
      plans={[
        { t: 0, x: 960, y: 540, zoom: 1 },
        { t: T.site - 0.25, x: 520, y: 560, zoom: 1.6 }, // le site et son FortiGate
        { t: T.acces - 0.3, x: 700, y: 560, zoom: 1.25 }, // les deux opérateurs
        { t: T.tunnels - 0.2, x: 960, y: 540, zoom: 1 }, // tout le schéma
        { t: T.etSi + 0.3, x: 700, y: 450, zoom: 1.4 }, // la ligne A (les centres de données sortent du cadre en entier)
        { t: T.bascule, x: 960, y: 540, zoom: 1 },
      ]}
    >
      <Schema />
      {/* Au cœur du schéma : le nom de la technique, puis le temps de bascule */}
      <Entree t={T.sdwan} fin={T.etSi} style={{ left: 700, top: 440, width: 600, textAlign: "center" }}>
        <div style={{ fontSize: 88, fontWeight: 700, color: C.reseau, lineHeight: 1.1, whiteSpace: "nowrap" }}>SD-WAN</div>
      </Entree>
      <Entree t={T.pilote} fin={T.etSi} style={{ left: 700, top: 560, width: 600, textAlign: "center", fontSize: 40, lineHeight: 1.25, color: C.doux }}>
        réseau étendu
        <br />
        piloté par logiciel
      </Entree>
      <Entree t={T.moins} style={{ left: 700, top: 425, width: 600, textAlign: "center" }}>
        <div style={{ fontSize: 130, fontWeight: 700, lineHeight: 1.1, whiteSpace: "nowrap" }}>
          <Compteur valeur={3.8} t={T.moins} duree={1} decimales={1} /> s
        </div>
        <div style={{ fontSize: 40, lineHeight: 1.25, color: C.doux }}>
          mesurées sur
          <br />
          notre maquette
        </div>
      </Entree>
    </Camera>
    <Son t={T.moins} fichier="compteur.wav" />

    <Briques />
    <Repere t={T.site} numero={1}>
      Relier les sites
    </Repere>
  </Scene>
);
