import { DUREE_SCENE_1, Scene1 } from "./Scene1";
import { DUREE_SCENE_2, Scene2 } from "./Scene2";
import { DUREE_SCENE_3, Scene3 } from "./Scene3";
import { DUREE_SCENE_4A, Scene4a } from "./Scene4a";
import { DUREE_SCENE_4B, Scene4b } from "./Scene4b";
import { DUREE_SCENE_4C, Scene4c } from "./Scene4c";
import { DUREE_SCENE_4D, Scene4d } from "./Scene4d";
import { DUREE_SCENE_5, Scene5 } from "./Scene5";
import { DUREE_SCENE_6, Scene6 } from "./Scene6";
import { DUREE_SCENE_7, Scene7 } from "./Scene7";
import { DUREE_SCENE_8, Scene8 } from "./Scene8";
import { DUREE_SCENE_9, Scene9 } from "./Scene9";

// Les scènes dans l'ordre de la vidéo. `duree` est en secondes et vient de la voix.
export const SCENES = [
  { id: "01", nom: "Scène 1 : l'accroche", Composant: Scene1, duree: DUREE_SCENE_1 },
  { id: "02", nom: "Scène 2 : le client", Composant: Scene2, duree: DUREE_SCENE_2 },
  { id: "03", nom: "Scène 3 : ce que le client va noter", Composant: Scene3, duree: DUREE_SCENE_3 },
  { id: "04a", nom: "Scène 4a : relier les sites", Composant: Scene4a, duree: DUREE_SCENE_4A },
  { id: "04b", nom: "Scène 4b : deux centres de données", Composant: Scene4b, duree: DUREE_SCENE_4B },
  { id: "04c", nom: "Scène 4c : filtrer chaque échange", Composant: Scene4c, duree: DUREE_SCENE_4C },
  { id: "04d", nom: "Scène 4d : ceux qui travaillent à distance", Composant: Scene4d, duree: DUREE_SCENE_4D },
  { id: "05", nom: "Scène 5 : combien ça coûte", Composant: Scene5, duree: DUREE_SCENE_5 },
  { id: "06", nom: "Scène 6 : la preuve", Composant: Scene6, duree: DUREE_SCENE_6 },
  { id: "07", nom: "Scène 7 : les limites que nous assumons", Composant: Scene7, duree: DUREE_SCENE_7 },
  { id: "08", nom: "Scène 8 : l'équipe", Composant: Scene8, duree: DUREE_SCENE_8 },
  { id: "09", nom: "Scène 9 : la fin", Composant: Scene9, duree: DUREE_SCENE_9 },
];
