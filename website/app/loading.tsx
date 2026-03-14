import { GooeyLoader } from 'components/ui/loader-10';

export default function Loading() {
  return (
    <div className="flex h-[100dvh] w-full flex-col items-center justify-center">
      <GooeyLoader
        primaryColor="hsl(0 72% 51%)"
        secondaryColor="hsl(0 84% 60%)"
        borderColor="hsl(var(--border))"
      />
    </div>
  );
}
