import React from "react";
import { Apparait, Camera, Entree, Paquets, Trait, chemin, type Courbe, type Pt } from "../anim";
import { Base, Coche, Croix, Etiquette, Nuage, Personne, Pop, Repere } from "../elements";
import { Scene, charger } from "../Scene";
import { C } from "../theme";

// Scène 4c, « filtrer chaque échange » : Internet, le pare-feu de périmètre, la zone tampon, le pare-feu interne
// et les cinq zones. Un paquet passe (vert), un autre est stoppé devant la base (croix rouge), l'administrateur
// passe par le bastion.
const S = charger("04c");
const a = S.a;
const T = {
  brique: a("Troisième brique"),
  internet: a("d'Internet"),
  arrete: a("s'arrête"),
  tampon: a("zone tampon"),
  dmz: a("D-M-Z"),
  waf: a("pare-feu applicatif"),
  bloque: a("bloque"),
  second: a("second pare-feu"),
  cinq: a("cinq zones"),
  interdit: a("tout est interdit"),
  sauf: a("sauf ce qui"),
  web: a("Le serveur web"),
  application: a("l'application"),
  jamais: a("jamais directement"),
  base: a("la base de données"),
  admins: a("les administrateurs"),
  bastion: a("un bastion"),
  trace: a("trace chaque action"),
};
export const DUREE_SCENE_4C = S.duree;

// Géométrie, dans l'image 1920 × 1080.
const MILIEU = 560; // axe horizontal du schéma
const ZONES = [
  { nom: "Applications", y: 200 },
  { nom: "Données", y: 370 },
  { nom: "Administration", y: 540 },
  { nom: "Partenaires", y: 710 },
];
const [APPLICATION, DONNEES, BASTION] = ZONES.map((z) => z.y + 75); // axe de l'équipement de chaque zone
const droite = (de: Pt, vers: Pt): Courbe => [
  de,
  [de[0] + (vers[0] - de[0]) / 3, de[1] + (vers[1] - de[1]) / 3],
  [de[0] + ((vers[0] - de[0]) * 2) / 3, de[1] + ((vers[1] - de[1]) * 2) / 3],
  vers,
];
const courbe = (de: Pt, vers: Pt): Courbe => [de, [(de[0] + vers[0]) / 2, de[1]], [(de[0] + vers[0]) / 2, vers[1]], vers];
// Les trajets des paquets.
const ENTREE: Courbe[] = [droite([250, MILIEU], [341, MILIEU]), droite([341, MILIEU], [520, MILIEU])];
const ATTAQUE: Courbe[] = [droite([250, 530], [341, 530]), courbe([341, 530], [540, 445])];
const VERS_APPLICATION: Courbe[] = [courbe([900, 595], [1008, MILIEU]), droite([1008, MILIEU], [1092, MILIEU]), courbe([1092, MILIEU], [1560, APPLICATION])];
const VERS_BASE: Courbe[] = [courbe([900, 595], [1008, 600]), droite([1008, 600], [1092, 600]), courbe([1092, 600], [1570, DONNEES])];
const VERS_BASTION: Courbe[] = [droite([1690, 880], [1690, BASTION + 54])];

/** Pare-feu : un mur, avec son nom en dessous. */
const PareFeu: React.FC<{ t: number; x: number; nom: string }> = ({ t, x, nom }) => (
  <Pop t={t} x={x} y={MILIEU}>
    <rect x={-42} y={-125} width={84} height={250} rx={12} fill={C.panneau} stroke={C.reseau} strokeWidth={5} />
    {[-62, 0, 62].map((y) => (
      <line key={y} x1={-42} x2={42} y1={y} y2={y} stroke={C.reseau} strokeWidth={4} />
    ))}
    <Etiquette x={0} y={182} taille={36}>
      Pare-feu
    </Etiquette>
    <Etiquette x={0} y={226} taille={36}>
      {nom}
    </Etiquette>
  </Pop>
);

/** Boîte d'un équipement, avec son nom sur une ou deux lignes. */
const Boite: React.FC<{ t: number; x: number; y: number; largeur?: number; lignes: string[] }> = ({ t, x, y, largeur = 350, lignes }) => (
  <Pop t={t} x={x} y={y}>
    <rect x={-largeur / 2} y={-50} width={largeur} height={100} rx={14} fill={C.panneau} stroke={C.texte} strokeWidth={4} />
    {lignes.map((ligne, i) => (
      <Etiquette key={ligne} x={0} y={(lignes.length === 1 ? 13 : -8) + i * 40} taille={36}>
        {ligne}
      </Etiquette>
    ))}
  </Pop>
);

const Pastille: React.FC<{ t: number; x: number; y: number; numero: number }> = ({ t, x, y, numero }) => (
  <Pop t={t} x={x} y={y}>
    <circle r={26} fill={C.reseau} />
    <Etiquette x={0} y={13} taille={36} gras couleur={C.fond}>
      {numero}
    </Etiquette>
  </Pop>
);

const Schema: React.FC = () => (
  <svg viewBox="0 0 1920 1080" style={{ position: "absolute", inset: 0 }}>
    {/* Ce qui vient d'Internet s'arrête dans la zone tampon */}
    <Pop t={T.internet} x={170} y={MILIEU}>
      <Nuage />
      <Etiquette x={0} y={110} taille={36}>
        Internet
      </Etiquette>
    </Pop>
    <Paquets route={ENTREE} debut={T.internet + 0.4} fin={T.waf} periode={0.8} trajet={1.3} couleur={C.texte} />
    <PareFeu t={T.arrete} x={385} nom="de périmètre" />

    {/* La zone tampon et ce qu'elle contient */}
    <Trait d="M 544 250 H 906 a 24 24 0 0 1 24 24 V 846 a 24 24 0 0 1 -24 24 H 544 a 24 24 0 0 1 -24 -24 V 274 a 24 24 0 0 1 24 -24 Z" t={T.tampon} duree={1.1} stroke={C.doux} strokeWidth={4} />
    <Boite t={T.waf} x={725} y={445} lignes={["Pare-feu", "applicatif web"]} />
    <Boite t={T.web} x={725} y={595} lignes={["Serveur web"]} />
    <Boite t={T.waf + 0.3} x={725} y={745} lignes={["Passerelle de", "transfert chiffré"]} />

    {/* Une attaque web : bloquée par le pare-feu applicatif */}
    <Paquets route={ATTAQUE} debut={T.bloque - 0.9} fin={T.bloque - 0.8} trajet={0.9} couleur={C.refus} />
    <Croix t={T.bloque} x={540} y={445} />

    {/* Le second pare-feu et les zones du centre de données */}
    <PareFeu t={T.second} x={1050} nom="interne" />
    {ZONES.map(({ nom, y }, i) => (
      <Pop key={nom} t={T.cinq + (i + 1) * 0.12} x={1510} y={y + 75}>
        <rect x={-330} y={-75} width={660} height={150} rx={20} fill={C.panneau} stroke={C.bord} strokeWidth={4} />
      </Pop>
    ))}
    <Pastille t={T.cinq} x={930} y={250} numero={1} />
    {ZONES.map(({ y }, i) => (
      <Pastille key={y} t={T.cinq + (i + 1) * 0.12} x={1840} y={y} numero={i + 2} />
    ))}
    <Boite t={T.application - 0.9} x={1690} y={APPLICATION} largeur={260} lignes={["Application"]} />
    <Pop t={T.base - 1.2} x={1690} y={DONNEES}>
      <g transform="scale(0.85)">
        <Base />
      </g>
    </Pop>

    {/* Autorisé : le serveur web parle à l'application */}
    <Trait d={chemin(VERS_APPLICATION)} t={T.web + 0.5} duree={1.2} stroke={C.ok} strokeWidth={5} />
    <Paquets route={VERS_APPLICATION} debut={T.web + 0.5} fin={T.jamais - 0.6} periode={0.7} trajet={1.4} couleur={C.ok} />
    <Coche t={T.application + 0.5} x={1520} y={APPLICATION - 40} taille={20} />

    {/* Refusé : jamais directement à la base de données */}
    <Trait d={chemin(VERS_BASE)} t={T.jamais} duree={1.2} stroke={C.refus} strokeWidth={5} />
    <Paquets route={VERS_BASE} debut={T.jamais} fin={T.jamais + 0.1} trajet={1.2} couleur={C.refus} />
    <Croix t={T.base} x={1585} y={DONNEES} />

    {/* L'administrateur passe par le bastion */}
    <Boite t={T.bastion} x={1690} y={BASTION} largeur={260} lignes={["Bastion"]} />
    <Trait d={chemin(VERS_BASTION)} t={T.bastion - 0.5} duree={0.9} stroke={C.ok} strokeWidth={5} />
    <Paquets route={VERS_BASTION} debut={T.bastion - 0.5} fin={S.duree} periode={0.9} trajet={1.1} couleur={C.ok} />
    <Pop t={T.admins} x={1690} y={925}>
      <Personne />
    </Pop>

    {/* Le nom des zones, par-dessus les trajets : un liseré de la couleur du fond le détache des traits */}
    {ZONES.map(({ nom, y }, i) => (
      <Pop key={nom} t={T.cinq + (i + 1) * 0.12} x={1210} y={y + 46}>
        <text fontSize={38} fontWeight={700} fill={C.texte} stroke={C.panneau} strokeWidth={12} strokeLinejoin="round" paintOrder="stroke">
          {nom}
        </text>
      </Pop>
    ))}
  </svg>
);

export const Scene4c: React.FC = () => (
  <Scene de={S}>
    <Camera
      plans={[
        { t: 0, x: 960, y: 540, zoom: 1 },
        { t: T.internet - 0.3, x: 480, y: 560, zoom: 1.45 }, // Internet, le périmètre, la zone tampon
        // Ensuite, tout le schéma : un zoom plus serré couperait des étiquettes au bord de l'image.
        { t: T.second - 0.3, x: 960, y: 540, zoom: 1 },
      ]}
    >
      <Schema />
      <Entree t={T.tampon} style={{ left: 550, top: 268, fontSize: 36, color: C.doux, whiteSpace: "nowrap" }}>
        <Apparait t={T.dmz} style={{ fontSize: 44, fontWeight: 700, color: C.texte, marginRight: 18 }}>
          DMZ
        </Apparait>
        zone tampon
      </Entree>
      <Entree t={T.trace} dy={0} style={{ left: 1210, top: 620, fontSize: 36, color: C.ok, whiteSpace: "nowrap" }}>
        action tracée
      </Entree>
    </Camera>

    {/* La règle, en haut de l'image */}
    <Entree t={T.interdit} fin={T.admins - 0.3} style={{ left: 760, top: 52, fontSize: 48, fontWeight: 700, lineHeight: 1.2, whiteSpace: "nowrap" }}>
      <span style={{ color: C.refus }}>Tout est interdit,</span>
      <br />
      <Apparait t={T.sauf} style={{ color: C.ok }}>
        sauf ce qui est autorisé
      </Apparait>
    </Entree>
    <Repere t={T.brique} numero={3}>
      Filtrer chaque échange
    </Repere>
  </Scene>
);
