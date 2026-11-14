import { Composition, Folder } from "remotion";
import { FPS, images } from "./Scene";
import { SCENES } from "./scenes";
import { IMAGES_VIDEO, Video } from "./Video";

// Les durées viennent de la voix : elles sont calculées, pas saisies.
export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition id="Video" component={Video} durationInFrames={IMAGES_VIDEO} fps={FPS} width={1920} height={1080} />
      <Folder name="Scenes">
        {SCENES.map(({ id, Composant, duree }) => (
          <Composition key={id} id={`Scene-${id}`} component={Composant} durationInFrames={images(duree)} fps={FPS} width={1920} height={1080} />
        ))}
      </Folder>
    </>
  );
};
