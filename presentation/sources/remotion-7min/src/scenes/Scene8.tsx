import React from "react";
import { interpolateColors, useCurrentFrame, useVideoConfig } from "remotion";
import { Trait, ressort } from "../anim";
import { Etiquette } from "../elements";
import { Scene, charger } from "../Scene";
import { C } from "../theme";

// Scène 8, l'équipe : sept cartes dans l'ordre de passage, chacune avec un prénom et un rôle,
// puis trois flèches de retour pour la démonstration, les risques et la conclusion.
const S = charger("08");
const a = S.a;
const T = {
  sept: a("nous sommes sept"),
  reviennent: a("reviennent"),
};
export const DUREE_SCENE_8 = S.duree;

const EQUIPE = [
  { prenom: "Farah", role: ["chef de", "projet"], t: a("Farah"), tRole: a("pilote le projet"), couleur: C.texte },
  { prenom: "Valentin", role: ["réseau entre", "les sites"], t: a("Valentin"), tRole: a("le réseau entre"), couleur: C.reseau },
  { prenom: "Nolan", role: ["centres de", "données"], t: a("Nolan"), tRole: a("les centres de données"), couleur: C.texte },
  { prenom: "Fatih", role: ["filtrage des", "échanges"], t: a("Fatih"), tRole: a("le filtrage"), couleur: C.texte },
  { prenom: "Younes", role: ["exploitation", "et agences"], t: a("Younes"), tRole: a("l'exploitation"), couleur: C.texte },
  { prenom: "Maxime", role: ["accès Zéro", "Confiance"], t: a("Maxime"), tRole: a("l'accès"), couleur: C.zt },
  { prenom: "Diane", role: ["coûts"], t: a("Diane"), tRole: a("les coûts"), couleur: C.texte },
];
// Ceux qui reviennent à la fin : la carte, l'instant où la voix les rappelle, et ce qu'ils présentent.
const RETOURS = [
  { carte: 1, t: a("Valentin", 2), tQuoi: a("la démonstration"), quoi: "démonstration" },
  { carte: 4, t: a("Younes", 2), tQuoi: a("les risques"), quoi: "risques" },
  { carte: 0, t: a("Farah", 2), tQuoi: a("la conclusion"), quoi: "conclusion" },
];

const LARGEUR = 236;
const PAS = 254;
const HAUT = 300;
const HAUTEUR = 360;
const centre = (i: number) => 80 + i * PAS + LARGEUR / 2;
const RAIL = HAUT + HAUTEUR + 90;

const Cartes: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <>
      {EQUIPE.map((m, i) => {
        const pose = ressort(frame, fps, T.sept + i * 0.08, undefined, { damping: 14 });
        const fin = i + 1 < EQUIPE.length ? EQUIPE[i + 1].t : T.reviennent - 1.8;
        const retour = RETOURS.find((r) => r.carte === i);
        // La carte est mise en avant quand la voix nomme la personne, puis de nouveau si elle revient à la fin.
        const active = ressort(frame, fps, m.t) - ressort(frame, fps, fin) + (retour ? ressort(frame, fps, retour.t) : 0);
        const nommee = ressort(frame, fps, m.t, 0.5);
        const role = ressort(frame, fps, m.tRole, 0.5);
        return (
          <div
            key={m.prenom}
            style={{
              position: "absolute",
              left: 80 + i * PAS,
              top: HAUT,
              width: LARGEUR,
              height: HAUTEUR,
              boxSizing: "border-box",
              borderRadius: 24,
              background: C.panneau,
              border: `4px solid ${interpolateColors(active, [0, 1], [C.bord, m.couleur])}`,
              scale: pose * (1 + 0.07 * active),
              opacity: Math.min(1, pose * 3),
              textAlign: "center",
              whiteSpace: "nowrap",
            }}
          >
            <div
              style={{
                width: 104,
                height: 104,
                margin: "28px auto 16px",
                borderRadius: 52,
                background: interpolateColors(nommee, [0, 1], [C.bord, m.couleur]),
                color: C.fond,
                fontSize: 60,
                fontWeight: 700,
                lineHeight: "104px",
              }}
            >
              {i + 1}
            </div>
            <div style={{ fontSize: 46, fontWeight: 700, opacity: nommee }}>{m.prenom}</div>
            <div style={{ fontSize: 36, lineHeight: 1.25, marginTop: 10, color: C.doux, opacity: role * (0.6 + 0.4 * Math.min(1, active)) }}>
              {m.role.map((ligne) => (
                <div key={ligne}>{ligne}</div>
              ))}
            </div>
          </div>
        );
      })}
    </>
  );
};

const RetourTexte: React.FC<{ x: number; t: number; texte: string }> = ({ x, t, texte }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <Etiquette x={x} y={RAIL + 62} taille={36} gras opacity={ressort(frame, fps, t, 0.5)}>
      {texte}
    </Etiquette>
  );
};

export const Scene8: React.FC = () => (
  <Scene de={S}>
    <Cartes />
    <svg viewBox="0 0 1920 1080" style={{ position: "absolute", inset: 0 }}>
      {/* Le retour : un trait part de la dernière carte et remonte vers ceux qui reviennent */}
      <Trait d={`M ${centre(6)} ${HAUT + HAUTEUR + 16} V ${RAIL} H ${centre(0)}`} t={T.reviennent} duree={1.2} stroke={C.doux} strokeWidth={5} strokeLinejoin="round" />
      {RETOURS.map((r) => (
        <React.Fragment key={r.quoi}>
          <Trait
            d={`M ${centre(r.carte)} ${RAIL} V ${HAUT + HAUTEUR + 26} m -16 18 l 16 -18 l 16 18`}
            t={r.tQuoi - 0.4}
            duree={0.5}
            stroke={C.texte}
            strokeWidth={6}
            strokeLinejoin="round"
          />
          <RetourTexte x={centre(r.carte)} t={r.tQuoi} texte={r.quoi} />
        </React.Fragment>
      ))}
    </svg>
  </Scene>
);
