import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { Apparait, Entree, ressort } from "../anim";
import { Scene, charger } from "../Scene";
import { C } from "../theme";

// Scène 7, les limites que nous assumons : quatre cartes à liseré rouge arrivent l'une après l'autre.
// La carte dont parle la voix est dépliée ; les précédentes se replient sur leur titre.
const S = charger("07");
const a = S.a;
const T = {
  limites: a("ses limites"),
  quatre: a("assumons quatre"),
  c1: a("Le pare-feu prévu"),
  f600: a("le six cents F"),
  successeur: a("son successeur"),
  rechiffre: a("rechiffré"),
  c2: a("La licence"),
  des4: a("des quatre pare-feu"),
  incluse: a("n'est pas incluse"),
  c3: a("Le stockage"),
  extension: a("une extension"),
  c4: a("la certification"),
  hds: a("H-D-S"),
  obligatoire: a("pas forcément"),
  prudence: a("l'exigeons"),
};
export const DUREE_SCENE_7 = S.duree;

const CARTES = [
  { t: T.c1, tTitre: T.f600, titre: "FortiGate 600F", details: [{ t: T.successeur, texte: "successeur probable, le 700G" }, { t: T.rechiffre, texte: "rechiffré au devis" }] },
  { t: T.c2, tTitre: T.c2 + 0.2, titre: "Licence Zéro Confiance", details: [{ t: T.des4, texte: "des 4 pare-feu d'entrée" }, { t: T.incluse, texte: "non incluse" }] },
  { t: T.c3, tTitre: T.c3 + 0.2, titre: "Stockage", details: [{ t: T.extension, texte: "extension probable" }] },
  { t: T.c4, tTitre: T.hds, titre: "HDS", details: [{ t: T.obligatoire, texte: "pas forcément obligatoire" }, { t: T.prudence, texte: "exigé par prudence" }] },
];
const REPLIEE = 104;
const DEPLIEE = 320;
const ECART = 22;
const HAUT = 190;

const Cartes: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  // Une carte est dépliée de son arrivée jusqu'à l'arrivée de la suivante (la dernière le reste).
  const depliee = CARTES.map((c, i) => ressort(frame, fps, c.t) - (i + 1 < CARTES.length ? ressort(frame, fps, CARTES[i + 1].t) : 0));
  let top = HAUT;
  return (
    <>
      {CARTES.map((c, i) => {
        const arrivee = ressort(frame, fps, c.t);
        const hauteur = REPLIEE + (DEPLIEE - REPLIEE) * depliee[i];
        const y = top;
        top += hauteur + ECART;
        return (
          <div
            key={c.titre}
            style={{
              position: "absolute",
              left: 100,
              top: y,
              width: 1720,
              height: hauteur,
              boxSizing: "border-box",
              overflow: "hidden",
              padding: "20px 44px",
              borderRadius: 20,
              background: C.panneau,
              borderLeft: `14px solid ${C.refus}`,
              opacity: arrivee,
              translate: `${(1 - arrivee) * 160}px 0px`,
              whiteSpace: "nowrap",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 28, height: 64, fontSize: 56, fontWeight: 700 }}>
              <span style={{ color: C.refus }}>{i + 1}</span>
              <Apparait t={c.tTitre}>{c.titre}</Apparait>
            </div>
            <div style={{ marginTop: 26, marginLeft: 62, fontSize: 60, lineHeight: 1.35, color: C.doux, opacity: depliee[i] }}>
              {c.details.map((d) => (
                <Apparait key={d.texte} t={d.t} style={{ display: "block" }}>
                  {d.texte}
                </Apparait>
              ))}
            </div>
          </div>
        );
      })}
    </>
  );
};

export const Scene7: React.FC = () => (
  <Scene de={S}>
    {/* Le titre reste pendant la première carte, puis s'efface : jamais plus de douze mots à l'écran */}
    <Entree t={T.limites} fin={T.c2 - 0.2} style={{ left: 100, top: 60, fontSize: 84, fontWeight: 700, whiteSpace: "nowrap" }}>
      <Apparait t={T.quatre} style={{ color: C.refus, marginRight: 28 }}>
        4
      </Apparait>
      limites assumées
    </Entree>
    <Cartes />
  </Scene>
);
