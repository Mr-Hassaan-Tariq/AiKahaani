import { GooeyLoader } from 'components/ui/loader-10';

export default function Loading() {
  return (
    <div className="flex h-[100dvh] w-full flex-col items-center justify-center">
      <GooeyLoader
        primaryColor="#BAFF38"
        secondaryColor="#9fe32a"
        borderColor="hsl(var(--border))"
      />
    </div>
  );
}
