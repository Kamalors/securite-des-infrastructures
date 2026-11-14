import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { Apparait, Compteur, Entree, ressort, useRessort } from "../anim";
import { Cadenas, Pop } from "../elements";
import { Scene, Son, charger } from "../Scene";
import { C } from "../theme";

// Scène 2, le client : trois compteurs (sites, utilisateurs, partenaires), puis le dossier médical et son cadenas.
const S = charger("02");
const a = S.a;
const T = {
  client: a("grande mutuelle santé"),
  fictive: a("fictive"),
  sieges: a("Deux sièges"),
  agences: a("quatre cent"),
  etranger: a("trente à l'étranger"),
  utilisateurs: a("Dix mille utilisateurs"),
  partenaires: a("une centaine de partenaires"),
  acceder: a("accéder"),
  sensible: a("Le point sensible"),
  donnees: a("les données"),
  sante: a("informations de santé"),
  fuite: a("Une fuite"),
  effondre: a("s'effondre"),
  appel: a("appel d'offres"),
  securite: a("architecture de sécurité"),
  centres: a("ses centres de données"),
  agences2: a("ses agences"),
};
export const DUREE_SCENE_2 = S.duree;

const carte = (left: number, width: number): React.CSSProperties => ({
  left,
  top: 290,
  width,
  height: 520,
  boxSizing: "border-box",
  padding: "34px 44px",
  borderRadius: 28,
  background: C.panneau,
  border: `3px solid ${C.bord}`,
});
const chiffre: React.CSSProperties = { fontSize: 120, fontWeight: 700, lineHeight: 1.1, whiteSpace: "nowrap" };
const libelle: React.CSSProperties = { fontSize: 56, color: C.doux };
const ligne: React.CSSProperties = { display: "block", fontSize: 46, color: C.doux, marginTop: 14, whiteSpace: "nowrap" };
const gras: React.CSSProperties = { fontWeight: 700, color: C.texte };

/** Le total des sites monte au fil de la voix : 2 sièges, puis 498 agences, puis 30 à l'international. */
const TotalSites: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const total = 2 * ressort(frame, fps, T.sieges, 0.6) + 498 * ressort(frame, fps, T.agences, 1.2) + 30 * ressort(frame, fps, T.etranger, 0.8);
  return <span style={{ fontVariantNumeric: "tabular-nums" }}>{Math.round(total)}</span>;
};

/** Les partenaires n'accèdent qu'à certaines applications : deux tuiles sur quatre s'allument en vert. */
const Applications: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div style={{ display: "flex", gap: 18, marginTop: 44 }}>
      {[true, false, true, false].map((autorisee, i) => {
        const p = ressort(frame, fps, T.acceder + i * 0.1, undefined, { damping: 13 });
        return <div key={i} style={{ width: 76, height: 76, borderRadius: 16, scale: p, background: autorisee ? C.ok : C.bord }} />;
      })}
    </div>
  );
};

const Compteurs: React.FC = () => {
  const sortie = useRessort(T.sensible, 0.5);
  return (
    <div style={{ position: "absolute", inset: 0, opacity: 1 - sortie, translate: `0px ${-50 * sortie}px` }}>
      <Entree t={T.client} fin={T.sieges - 0.3} style={{ left: 100, top: 120, fontSize: 84, fontWeight: 700, whiteSpace: "nowrap" }}>
        Une grande mutuelle santé
        <Apparait t={T.fictive} style={{ marginLeft: 36, padding: "6px 30px", borderRadius: 50, border: `3px solid ${C.doux}`, fontSize: 48, fontWeight: 400, color: C.doux, verticalAlign: "middle" }}>
          fictive
        </Apparait>
      </Entree>

      <Entree t={T.sieges} style={carte(100, 660)}>
        <div style={chiffre}>
          <TotalSites /> <span style={{ ...libelle, fontWeight: 400 }}>sites</span>
        </div>
        <Apparait t={T.sieges} style={ligne}>
          <span style={gras}>2</span> sièges
        </Apparait>
        <Apparait t={T.agences} style={ligne}>
          <span style={gras}>498</span> agences en France
        </Apparait>
        <Apparait t={T.etranger} style={ligne}>
          <span style={gras}>30</span> à l'international
        </Apparait>
      </Entree>

      <Entree t={T.utilisateurs} style={carte(800, 500)}>
        <div style={chiffre}>
          <Compteur valeur={10000} t={T.utilisateurs} duree={1} />
        </div>
        <div style={libelle}>utilisateurs</div>
      </Entree>

      <Entree t={T.partenaires} style={carte(1340, 480)}>
        <div style={chiffre}>
          ≈ <Compteur valeur={100} t={T.partenaires} duree={1} />
        </div>
        <div style={libelle}>partenaires</div>
        <Applications />
      </Entree>
    </div>
  );
};

/** Le dossier médical : il tremble à « une fuite », s'affaisse à « s'effondre », puis le cadenas se ferme. */
const Dossier: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const secousse = ressort(frame, fps, T.fuite, undefined, { damping: 4, stiffness: 160 }) - ressort(frame, fps, T.fuite);
  const chute = ressort(frame, fps, T.effondre, undefined, { damping: 8 }) - ressort(frame, fps, T.securite);
  const ferme = Math.min(1, Math.max(0, ressort(frame, fps, T.securite, undefined, { damping: 11, stiffness: 220 })));
  return (
    <svg viewBox="0 0 1920 1080" style={{ position: "absolute", inset: 0 }}>
      <Pop t={T.donnees} x={500} y={540}>
        <g transform={`translate(0 ${30 * chute}) rotate(${9 * secousse - 8 * chute})`}>
          <path d="M -150 -190 H 90 L 150 -130 V 190 H -150 Z" fill={C.panneau} stroke={C.texte} strokeWidth={6} strokeLinejoin="round" />
          <path d="M 90 -190 V -130 H 150" fill="none" stroke={C.texte} strokeWidth={6} strokeLinejoin="round" />
          <path d="M -24 -120 h 48 v 36 h 36 v 48 h -36 v 36 h -48 v -36 h -36 v -48 h 36 z" fill={C.texte} />
          {[50, 95, 140].map((y) => (
            <rect key={y} x={-100} y={y} width={y === 140 ? 120 : 200} height={14} rx={7} fill={C.doux} />
          ))}
        </g>
      </Pop>
      <Pop t={T.fuite} x={640} y={690}>
        <g transform="scale(1.7)">
          <Cadenas ouvert={1 - ferme} />
        </g>
      </Pop>
    </svg>
  );
};

const etiquette: React.CSSProperties = { padding: "10px 36px", borderRadius: 50, fontSize: 52, whiteSpace: "nowrap", background: C.panneau };

export const Scene2: React.FC = () => (
  <Scene de={S}>
    <Compteurs />
    <Son t={T.sieges} fichier="compteur.wav" />
    <Son t={T.utilisateurs} fichier="compteur.wav" />
    <Son t={T.partenaires} fichier="compteur.wav" />

    <Dossier />
    <Entree t={T.sante} style={{ left: 780, top: 330, fontSize: 96, fontWeight: 700, whiteSpace: "nowrap" }}>
      Données de santé
    </Entree>
    <Entree t={T.appel} style={{ left: 780, top: 500, ...etiquette, border: `3px solid ${C.texte}` }}>
      Appel d'offres
    </Entree>
    <Entree t={T.centres} style={{ left: 780, top: 640, ...etiquette, border: `3px solid ${C.reseau}` }}>
      Centres de données
    </Entree>
    <Entree t={T.agences2} style={{ left: 1390, top: 640, ...etiquette, border: `3px solid ${C.reseau}` }}>
      Agences
    </Entree>
  </Scene>
);
