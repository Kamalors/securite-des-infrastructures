import { TransitionSeries, springTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import React from "react";
import plan from "./plan.json";
import { FPS, Son, TRANSITION, images } from "./Scene";
import { SCENES } from "./scenes";

// La vidéo complète : les scènes s'enchaînent avec une transition et un léger effet sonore.
// Un nouveau chapitre arrive en glissant ; les quatre briques de la scène 4 s'enchaînent en fondu.
const CHAPITRES = new Set(plan.scenes.filter((s) => "chapitre" in s).map((s) => s.id));
const timing = springTiming({ config: { damping: 200 }, durationInFrames: TRANSITION });

export const IMAGES_VIDEO = SCENES.reduce((total, s) => total + images(s.duree), 0) - (SCENES.length - 1) * TRANSITION;

export const Video: React.FC = () => {
  let fin = 0; // image où se termine la scène précédente
  const sons: React.ReactNode[] = [];
  const serie = SCENES.flatMap(({ id, nom, Composant, duree }, i) => {
    const sequence = (
      <TransitionSeries.Sequence key={id} name={nom} durationInFrames={images(duree)}>
        <Composant />
      </TransitionSeries.Sequence>
    );
    if (i === 0) {
      fin = images(duree);
      return [sequence];
    }
    sons.push(<Son key={id} t={(fin - TRANSITION) / FPS} fichier="transition.wav" volume={0.35} />);
    fin += images(duree) - TRANSITION;
    return [
      CHAPITRES.has(id) ? (
        <TransitionSeries.Transition key={`vers-${id}`} presentation={slide({ direction: "from-right" })} timing={timing} />
      ) : (
        <TransitionSeries.Transition key={`vers-${id}`} presentation={fade()} timing={timing} />
      ),
      sequence,
    ];
  });
  return (
    <>
      <TransitionSeries>{serie}</TransitionSeries>
      {sons}
    </>
  );
};
