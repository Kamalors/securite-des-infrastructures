import React from "react";
import { interpolateColors, useCurrentFrame, useVideoConfig } from "remotion";
import { Apparait, Compteur, Entree, Paquets, Trait, ressort, type Courbe, type Pt } from "../anim";
import { Coche, Croix, Etiquette, Pop } from "../elements";
import { Scene, Son, charger } from "../Scene";
import { C } from "../theme";

// Scène 6, la preuve : la maquette (7 équipements réseau, 8 serveurs et postes), les 17 tests qui se cochent,
// la bascule rejouée et son chronomètre, puis le bandeau sur ce que la maquette prouve.
const S = charger("06");
const a = S.a;
const T = {
  dossier: a("contentés d'un dossier"),
  maquette: a("une maquette"),
  quinze: a("quinze machines"),
  siege: a("un siège"),
  agence: a("une agence"),
  partenaire: a("un partenaire"),
  operateurs: a("les opérateurs"),
  centres: a("les centres de données"),
  tests: a("Dix-sept tests"),
  autorises: a("autorisés"),
  interdits: a("les interdits"),
  resultat: a("dix-sept sur dix-sept"),
  coupe: a("On coupe"),
  operateur: a("un opérateur"),
  bascule: a("le trafic bascule"),
  chrono: a("trois virgule huit"),
  prouve: a("prouve nos principes"),
  produits: a("pas les produits"),
};
export const DUREE_SCENE_6 = S.duree;

// La maquette, d'après docs/MAQUETTE.md : 7 équipements réseau (passerelles du siège, de l'agence et du partenaire,
// deux opérateurs, pare-feu des deux centres de données) et 8 serveurs et postes.
const SIEGE: Pt = [220, 300];
const AGENCE: Pt = [220, 540];
const PARTENAIRE: Pt = [220, 760];
const OP_A: Pt = [580, 400];
const OP_B: Pt = [580, 680];
const DC1: Pt = [940, 400];
const DC2: Pt = [940, 680];
const RESEAU = [SIEGE, AGENCE, PARTENAIRE, OP_A, OP_B, DC1, DC2];
const POSTES: Pt[] = [
  [100, 500], // deux postes à l'agence
  [100, 580],
  [580, 250], // un poste sur Internet
  [1080, 240], // cinq serveurs dans le premier centre de données
  [1080, 320],
  [1080, 400],
  [1080, 480],
  [1080, 560],
];
const LIENS: [Pt, Pt][] = [
  [SIEGE, OP_A],
  [SIEGE, OP_B],
  [AGENCE, OP_A],
  [AGENCE, OP_B],
  [PARTENAIRE, OP_A],
  [OP_A, DC1],
  [OP_A, DC2],
  [OP_B, DC1],
  [OP_B, DC2],
  [OP_A, OP_B],
  [POSTES[0], AGENCE],
  [POSTES[1], AGENCE],
  [POSTES[2], OP_A],
  ...POSTES.slice(3).map((p): [Pt, Pt] => [DC1, p]),
];
const droite = (de: Pt, vers: Pt): Courbe => [
  de,
  [de[0] + (vers[0] - de[0]) / 3, de[1] + (vers[1] - de[1]) / 3],
  [de[0] + ((vers[0] - de[0]) * 2) / 3, de[1] + ((vers[1] - de[1]) * 2) / 3],
  vers,
];
const PAR_A: Courbe[] = [droite(AGENCE, OP_A), droite(OP_A, DC1)];
const PAR_B: Courbe[] = [droite(AGENCE, OP_B), droite(OP_B, DC1)];

const Maquette: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const coupe = ressort(frame, fps, T.operateur, 0.5);
  return (
    <svg viewBox="0 0 1920 1080" style={{ position: "absolute", inset: 0 }}>
      {LIENS.map(([de, vers], i) => {
        const parA = de === OP_A || vers === OP_A;
        return (
          <Trait
            key={i}
            d={`M ${de.join(" ")} L ${vers.join(" ")}`}
            t={T.quinze + 0.6 + i * 0.04}
            duree={0.6}
            stroke={parA ? interpolateColors(coupe, [0, 1], [C.reseau, C.refus]) : C.reseau}
            strokeWidth={4}
            opacity={parA ? 0.7 - 0.35 * coupe : 0.7}
          />
        );
      })}
      {/* Le trafic de l'agence : par l'opérateur A, puis par B après la coupure */}
      <Paquets route={PAR_A} debut={T.centres + 0.6} fin={T.operateur - 0.2} periode={0.7} trajet={1.5} rayon={8} couleur="#d9fffd" />
      <Paquets route={PAR_B} debut={T.bascule + 0.4} fin={S.duree} periode={0.7} trajet={1.5} rayon={8} couleur="#d9fffd" />

      {RESEAU.map(([x, y], i) => (
        <Pop key={i} t={T.quinze + i * 0.06} x={x} y={y}>
          <rect x={-34} y={-34} width={68} height={68} rx={16} fill={C.panneau} stroke={i === 3 ? interpolateColors(coupe, [0, 1], [C.reseau, C.refus]) : C.reseau} strokeWidth={6} />
        </Pop>
      ))}
      {POSTES.map(([x, y], i) => (
        <Pop key={i} t={T.quinze + (7 + i) * 0.06} x={x} y={y}>
          <rect x={-22} y={-22} width={44} height={44} rx={9} fill={C.texte} />
        </Pop>
      ))}
      <Croix t={T.operateur} x={OP_A[0]} y={OP_A[1]} taille={30} />

      <Pop t={T.siege} x={SIEGE[0]} y={SIEGE[1]}>
        <Etiquette x={0} y={-52} taille={36}>
          Siège
        </Etiquette>
      </Pop>
      <Pop t={T.agence} x={AGENCE[0]} y={AGENCE[1]}>
        <Etiquette x={0} y={-52} taille={36}>
          Agence
        </Etiquette>
      </Pop>
      <Pop t={T.partenaire} x={PARTENAIRE[0]} y={PARTENAIRE[1]}>
        <Etiquette x={0} y={88} taille={36}>
          Partenaire
        </Etiquette>
      </Pop>
      <Pop t={T.operateurs} x={580} y={800}>
        <Etiquette x={0} y={0} taille={36}>
          Opérateurs
        </Etiquette>
      </Pop>
      <Pop t={T.centres} x={990} y={800}>
        <Etiquette x={0} y={0} taille={36}>
          Centres de données
        </Etiquette>
      </Pop>

      {/* « Pas seulement un dossier » : des feuilles, qui s'effacent quand la maquette arrive */}
      <Pop t={T.dossier} fin={T.maquette} x={600} y={520}>
        {[-24, 0, 24].map((d) => (
          <rect key={d} x={-110 + d} y={-140 - d} width={220} height={280} rx={14} fill={C.panneau} stroke={C.texte} strokeWidth={5} />
        ))}
        {[-70, -20, 30].map((y) => (
          <rect key={y} x={-56} y={y - 24} width={160} height={14} rx={7} fill={C.doux} />
        ))}
      </Pop>
    </svg>
  );
};

/** Les 17 tests : une ligne se coche après l'autre, et le compteur suit. */
const Tests: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pas = (T.resultat - 0.4 - T.autorises) / 17;
  const instant = (k: number) => T.autorises + k * pas;
  const coches = Array.from({ length: 17 }, (_, k) => k).filter((k) => frame >= instant(k) * fps).length;
  const final = ressort(frame, fps, T.resultat, undefined, { damping: 7 }) - ressort(frame, fps, T.resultat + 0.25);
  return (
    <Entree t={T.tests} fin={T.coupe - 0.3} style={{ left: 1260, top: 150, width: 580 }}>
      <div style={{ fontSize: 120, fontWeight: 700, lineHeight: 1.1, whiteSpace: "nowrap", scale: 1 + 0.12 * final, transformOrigin: "left center", fontVariantNumeric: "tabular-nums" }}>
        {coches} / 17
        <span style={{ fontSize: 52, fontWeight: 400, color: C.doux, marginLeft: 20 }}>tests</span>
      </div>
      <svg viewBox="0 0 580 520" style={{ width: 580, height: 520, marginTop: 14 }}>
        {Array.from({ length: 17 }, (_, k) => {
          const x = k < 9 ? 0 : 300;
          const y = 14 + (k % 9) * 56;
          return (
            <g key={k}>
              <rect x={x} y={y} width={40} height={40} rx={9} fill="none" stroke={C.doux} strokeWidth={4} />
              <rect x={x + 60} y={y + 11} width={190} height={18} rx={9} fill={C.bord} />
              <Coche t={instant(k)} x={x + 18} y={y + 22} taille={11} />
            </g>
          );
        })}
      </svg>
      <div style={{ fontSize: 36, lineHeight: 1.35, whiteSpace: "nowrap" }}>
        <Apparait t={T.autorises} style={{ display: "block" }}>
          <span style={{ color: C.ok }}>●</span> autorisé : passe
        </Apparait>
        <Apparait t={T.interdits} style={{ display: "block" }}>
          <span style={{ color: C.refus }}>●</span> interdit : bloqué, journalisé
        </Apparait>
      </div>
    </Entree>
  );
};

export const Scene6: React.FC = () => (
  <Scene de={S}>
    {/* La maquette reste à gauche ; la droite accueille tour à tour le compte des machines, les tests et le chronomètre */}
    <Maquette />

    <Entree t={T.quinze} fin={T.tests - 0.3} style={{ left: 1260, top: 330, width: 580, textAlign: "center", fontSize: 56, color: C.doux, whiteSpace: "nowrap" }}>
      <div style={{ fontSize: 210, fontWeight: 700, lineHeight: 1.1, color: C.texte }}>
        <Compteur valeur={15} t={T.quinze} duree={1} />
      </div>
      machines
    </Entree>
    <Son t={T.quinze} fichier="compteur.wav" />

    <Tests />
    <Son t={T.autorises} fichier="compteur.wav" />

    {/* La bascule rejouée */}
    <Entree t={T.chrono} style={{ left: 1260, top: 330, width: 580, textAlign: "center", whiteSpace: "nowrap" }}>
      <div style={{ fontSize: 210, fontWeight: 700, lineHeight: 1.1 }}>
        <Compteur valeur={3.8} t={T.chrono} duree={1} decimales={1} /> s
      </div>
      <div style={{ fontSize: 56, color: C.doux }}>de bascule</div>
    </Entree>
    <Son t={T.chrono} fichier="compteur.wav" />

    {/* Ce que la maquette prouve, et ce qu'elle ne prouve pas : une limite, donc un liseré rouge */}
    <Entree
      t={T.prouve}
      style={{ left: 80, top: 880, padding: "16px 40px", borderRadius: 18, background: C.panneau, borderLeft: `12px solid ${C.refus}`, fontSize: 56, fontWeight: 700, whiteSpace: "nowrap" }}
    >
      prouve nos principes,
      <Apparait t={T.produits}> pas les produits</Apparait>
    </Entree>
  </Scene>
);
