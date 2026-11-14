import React from "react";
import { Compteur, Entree } from "../anim";
import { Scene, Son, charger } from "../Scene";
import { C } from "../theme";

// Scène 9, la fin : la phrase de conclusion, puis les trois chiffres à retenir et la mention de la voix.
const S = charger("09");
const a = S.a;
const T = {
  sites: a("Cinq cent trente"),
  prix: a("un prix au mois"),
  preuves: a("des preuves"),
  reponse: a("Voilà notre réponse"),
};
export const DUREE_SCENE_9 = S.duree;

const carte = (left: number): React.CSSProperties => ({
  left,
  top: 520,
  width: 540,
  height: 270,
  boxSizing: "border-box",
  padding: "34px 40px",
  borderRadius: 28,
  background: C.panneau,
  border: `3px solid ${C.bord}`,
  fontSize: 46,
  color: C.doux,
  whiteSpace: "nowrap",
});
const chiffre: React.CSSProperties = { fontSize: 88, fontWeight: 700, lineHeight: 1.15, color: C.texte };

export const Scene9: React.FC = () => (
  <Scene de={S}>
    <Entree t={T.sites} style={{ left: 120, top: 190, fontSize: 92, fontWeight: 700, lineHeight: 1.2, whiteSpace: "nowrap" }}>
      Une architecture sécurisée
      <br />
      pour 530 sites, en abonnement
    </Entree>

    <Entree t={T.prix} style={carte(120)}>
      <div style={chiffre}>
        <Compteur valeur={221424} t={T.prix} duree={1} /> €
      </div>
      HT / mois
    </Entree>
    <Son t={T.prix} fichier="compteur.wav" />
    <Entree t={T.preuves} style={carte(690)}>
      <div style={chiffre}>
        <Compteur valeur={17} t={T.preuves} duree={0.8} /> / 17
      </div>
      tests
    </Entree>
    <Entree t={T.preuves + 0.3} style={carte(1260)}>
      <div style={chiffre}>
        <Compteur valeur={3.8} t={T.preuves + 0.3} duree={0.8} decimales={1} /> s
      </div>
      de bascule
    </Entree>

    {/* La licence du modèle de voix (CC BY 4.0) demande cette mention */}
    <Entree t={T.reponse + 0.8} dy={0} style={{ left: 120, top: 890, fontSize: 36, color: C.doux, whiteSpace: "nowrap" }}>
      Voix générée par intelligence artificielle (Kyutai TTS)
    </Entree>
  </Scene>
);
