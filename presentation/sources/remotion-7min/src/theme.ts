import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

// Couleurs fixes de la vidéo : chaque couleur a un seul sens.
export const C = {
  fond: "#0a0f1a",
  panneau: "#131c2e",
  bord: "#2b3854",
  texte: "#eef2f8",
  doux: "#9aa7bf",
  reseau: "#1fb8b3", // bleu canard : le réseau
  zt: "#ff8a3c", // orange : le Zéro Confiance
  refus: "#ff4d5a", // rouge : les refus et les limites
  ok: "#3ecf7a", // vert : ce qui est autorisé
} as const;

export const POLICE = "Instrument Sans";

loadFont({ family: POLICE, url: staticFile("fonts/InstrumentSans-Regular.ttf"), weight: "400" });
loadFont({ family: POLICE, url: staticFile("fonts/InstrumentSans-Bold.ttf"), weight: "700" });
