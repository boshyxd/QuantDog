import Iridescence from '../blocks/Backgrounds/Iridescence/Iridescence';

export default function Visual() {
  return (
    <div className="h-screen w-full">
      <Iridescence
        color={[1, 1, 1]}
        mouseReact={false}
        amplitude={0.1}
        speed={1.0}
      />
    </div>
  );
}