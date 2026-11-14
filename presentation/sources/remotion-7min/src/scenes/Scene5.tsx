import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { Apparait, Compteur, Entree, ressort } from "../anim";
import { Etiquette } from "../elements";
import { Scene, Son, charger } from "../Scene";
import { C } from "../theme";

// Scène 5, combien ça coûte : le prix mensuel, le prix par utilisateur et par site, le coût total,
// puis la balance entre l'achat et l'abonnement.
const S = charger("05");
const a = S.a;
const T = {
  question: a("Combien ça coûte"),
  prix: a("deux cent vingt"),
  ht: a("hors taxes"),
  duree: a("sur trois ans"),
  chacun: a("Rapporté à chacun"),
  utilisateur: a("vingt-deux euros"),
  site: a("et par mois"),
  total: a("Sur trente-six mois"),
  huit: a("près de huit"),
  abonnement: a("L'abonnement coûte"),
  achat: a("l'achat"),
  surcout: a("quatre cent soixante-dix"),
  capex: a("quatre virgule deux"),
  depart: a("dès le départ"),
  demandait: a("C'est exactement"),
};
export const DUREE_SCENE_5 = S.duree;

const centre: React.CSSProperties = { left: 0, width: 1920, textAlign: "center", whiteSpace: "nowrap" };
const carte = (left: number): React.CSSProperties => ({
  left,
  top: 340,
  width: 760,
  height: 360,
  boxSizing: "border-box",
  padding: "50px 56px",
  borderRadius: 28,
  background: C.panneau,
  border: `3px solid ${C.bord}`,
  fontSize: 46,
  color: C.doux,
  whiteSpace: "nowrap",
});
const grand: React.CSSProperties = { fontSize: 130, fontWeight: 700, lineHeight: 1.15, color: C.texte };

// La balance : le fléau tourne autour du pivot, les plateaux pendent à ses extrémités.
const PIVOT = { x: 960, y: 300 };
const BRAS = 420;

const Balance: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const visible = ressort(frame, fps, T.abonnement, 0.6);
  // Penche d'abord un peu vers l'achat (l'abonnement coûte plus cher), puis nettement vers l'abonnement (rien à avancer).
  const angle =
    -4 * ressort(frame, fps, T.surcout, undefined, { damping: 9 }) +
    8 * ressort(frame, fps, T.capex, undefined, { damping: 9 }) +
    7 * ressort(frame, fps, T.demandait, undefined, { damping: 6, mass: 1.4 });
  const rad = (angle * Math.PI) / 180;
  const plateau = (sens: number) => ({ x: PIVOT.x + sens * BRAS * Math.cos(rad), y: PIVOT.y + sens * BRAS * Math.sin(rad) });
  const gauche = plateau(-1);
  const droite = plateau(1);
  const apparait = (t: number) => ressort(frame, fps, t, 0.5);
  return (
    <svg viewBox="0 0 1920 1080" style={{ position: "absolute", inset: 0, opacity: visible }}>
      <g stroke={C.texte} strokeWidth={8} strokeLinecap="round" fill="none">
        <path d={`M ${PIVOT.x} ${PIVOT.y} V 900 M 840 900 H 1080`} />
        <line x1={gauche.x} y1={gauche.y} x2={droite.x} y2={droite.y} />
        {[gauche, droite].map((p, i) => (
          <path key={i} d={`M ${p.x} ${p.y} L ${p.x - 150} ${p.y + 130} H ${p.x + 150} Z`} strokeWidth={5} strokeLinejoin="round" />
        ))}
      </g>
      <circle cx={PIVOT.x} cy={PIVOT.y} r={16} fill={C.texte} />

      {/* L'achat, à gauche */}
      <g transform={`translate(${gauche.x} ${gauche.y})`}>
        <Etiquette x={0} y={-66} taille={60} gras opacity={apparait(T.achat)}>
          Achat
        </Etiquette>
        <g opacity={apparait(T.capex)}>
          <Etiquette x={0} y={232} taille={84} gras>
            4,22 M€
          </Etiquette>
          <Etiquette x={0} y={290} taille={44} couleur={C.doux}>
            à avancer
          </Etiquette>
        </g>
      </g>

      {/* L'abonnement, à droite */}
      <g transform={`translate(${droite.x} ${droite.y})`}>
        <Etiquette x={0} y={-66} taille={60} gras opacity={apparait(T.abonnement + 0.2)}>
          Abonnement
        </Etiquette>
        <g opacity={apparait(T.surcout)}>
          <Etiquette x={0} y={220} taille={64} gras>
            ≈ 470 000 €
          </Etiquette>
          <Etiquette x={0} y={272} taille={44} couleur={C.doux}>
            de plus sur 3 ans
          </Etiquette>
        </g>
        <Etiquette x={0} y={346} taille={56} gras opacity={apparait(T.depart)}>
          rien à avancer
        </Etiquette>
      </g>
    </svg>
  );
};

export const Scene5: React.FC = () => (
  <Scene de={S}>
    <Entree t={T.question} fin={T.prix - 0.4} style={{ ...centre, top: 440, fontSize: 130, fontWeight: 700 }}>
      Combien ça coûte ?
    </Entree>

    {/* 1. Le prix mensuel */}
    <Entree t={T.prix} fin={T.chacun} style={{ ...centre, top: 300 }}>
      <div style={{ fontSize: 210, fontWeight: 700, lineHeight: 1.1 }}>
        <Compteur valeur={221424} t={T.prix} duree={1.6} /> €
      </div>
      <div style={{ fontSize: 68, color: C.doux }}>
        <Apparait t={T.ht}>HT par mois</Apparait>
        <Apparait t={T.duree}>, sur 36 mois</Apparait>
      </div>
    </Entree>
    <Son t={T.prix} fichier="compteur.wav" />

    {/* 2. Rapporté à chacun */}
    <Entree t={T.utilisateur} fin={T.total - 0.2} style={carte(180)}>
      <div style={grand}>
        <Compteur valeur={22.14} t={T.utilisateur} duree={1} decimales={2} /> €
      </div>
      par utilisateur et par mois
    </Entree>
    <Entree t={T.site} fin={T.total - 0.2} style={carte(980)}>
      <div style={grand}>
        <Compteur valeur={418} t={T.site} duree={1} /> €
      </div>
      par site et par mois
    </Entree>
    <Son t={T.utilisateur} fichier="compteur.wav" />

    {/* 3. Le coût total */}
    <Entree t={T.total} fin={T.abonnement - 0.3} style={{ ...centre, top: 300, fontSize: 68, color: C.doux }}>
      Coût total sur 36 mois
      <div style={{ fontSize: 230, fontWeight: 700, lineHeight: 1.15, color: C.texte, opacity: 1 }}>
        <Apparait t={T.huit}>
          <Compteur valeur={7.97} t={T.huit} duree={1.2} decimales={2} /> M€
        </Apparait>
      </div>
    </Entree>
    <Son t={T.huit} fichier="compteur.wav" />

    {/* 4. Achat ou abonnement */}
    <Balance />
  </Scene>
);
