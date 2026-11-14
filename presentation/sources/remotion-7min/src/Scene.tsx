import { Audio } from "@remotion/media";
import React from "react";
import { AbsoluteFill, Sequence, staticFile, useVideoConfig } from "remotion";
import { instant, partie } from "./calage";
import plan from "./plan.json";
import { C, POLICE } from "./theme";
import v01 from "./voix/01.json";
import v02 from "./voix/02.json";
import v03 from "./voix/03.json";
import v04 from "./voix/04.json";
import v05 from "./voix/05.json";
import v06 from "./voix/06.json";
import v07 from "./voix/07.json";
import v08 from "./voix/08.json";
import v09 from "./voix/09.json";

// plan.json est la seule source du déroulé : il sert aussi aux chapitres et aux sous-titres (scripts/livraison.py).
export const FPS = plan.fps;
export const TRANSITION = plan.transition; // images ; égal au silence de début, pour que la voix parte quand l'image est en place
const DEBUT = plan.debut; // secondes de silence avant la voix
const FICHIERS = { "01": v01, "02": v02, "03": v03, "04": v04, "05": v05, "06": v06, "07": v07, "08": v08, "09": v09 };

/** Tout ce qu'une scène doit savoir de sa voix : le fichier, sa durée, et l'instant de chaque expression. */
export const charger = (id: string) => {
  const s = plan.scenes.find((x) => x.id === id);
  if (!s) throw new Error(`Scène inconnue : ${id}`);
  const voix = partie(FICHIERS[s.fichier as keyof typeof FICHIERS], id);
  return {
    voix,
    fichier: `${s.fichier}.mp3`,
    /** Durée de la scène en secondes : silence, voix, puis le temps de laisser l'image se poser. */
    duree: DEBUT + voix.duree + s.fin,
    /** Seconde de la scène où la voix commence à dire `expression`. */
    a: (expression: string, occurrence = 1) => DEBUT + instant(voix, expression, occurrence),
  };
};

/** Nombre d'images d'une durée. L'arrondi au millième évite qu'une erreur de virgule flottante ajoute une image ; scripts/livraison.py fait le même calcul. */
export const images = (secondes: number) => Math.ceil(Math.round(secondes * FPS * 1000) / 1000);

/** Fond sombre et voix off d'une scène. */
export const Scene: React.FC<{ de: ReturnType<typeof charger>; children: React.ReactNode }> = ({ de, children }) => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(circle at 42% 45%, #121c31 0%, ${C.fond} 72%)`,
        fontFamily: POLICE,
        color: C.texte,
      }}
    >
      {children}
      <Sequence name="Voix" layout="none" from={Math.round(DEBUT * fps)} durationInFrames={Math.ceil(de.voix.duree * fps)}>
        {/* Voix un peu sous son niveau maximal : ses crêtes, ajoutées à un effet sonore, ne saturent pas */}
        <Audio src={staticFile(`voix/${de.fichier}`)} trimBefore={Math.round(de.voix.debut * fps)} volume={0.8} />
      </Sequence>
    </AbsoluteFill>
  );
};

/** Effet sonore léger, à l'instant `t` (secondes). */
export const Son: React.FC<{ t: number; fichier: "compteur.wav" | "transition.wav"; volume?: number }> = ({
  t,
  fichier,
  volume = 0.3,
}) => {
  const { fps } = useVideoConfig();
  return (
    <Sequence name="Effet sonore" layout="none" from={Math.round(t * fps)}>
      <Audio src={staticFile(`sfx/${fichier}`)} volume={volume} />
    </Sequence>
  );
};
