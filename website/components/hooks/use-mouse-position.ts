import { RefObject, useEffect, useRef, useState } from 'react';

const THROTTLE_MS = 32; // ~30fps, reduces re-renders while keeping cursor responsive

export const useMousePosition = (containerRef?: RefObject<HTMLElement | SVGElement | null>) => {
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const lastUpdate = useRef(0);
  const rafRef = useRef<number>(0);

  useEffect(() => {
    const updatePosition = (x: number, y: number) => {
      const now = performance.now();
      if (now - lastUpdate.current < THROTTLE_MS) return;
      lastUpdate.current = now;

      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      rafRef.current = requestAnimationFrame(() => {
        if (containerRef?.current) {
          const rect = containerRef.current.getBoundingClientRect();
          setPosition({
            x: x - rect.left,
            y: y - rect.top,
          });
        } else {
          setPosition({ x, y });
        }
        rafRef.current = 0;
      });
    };

    const handleMouseMove = (ev: MouseEvent) => updatePosition(ev.clientX, ev.clientY);
    const handleTouchMove = (ev: TouchEvent) =>
      updatePosition(ev.touches[0].clientX, ev.touches[0].clientY);

    window.addEventListener('mousemove', handleMouseMove, { passive: true });
    window.addEventListener('touchmove', handleTouchMove, { passive: true });

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('touchmove', handleTouchMove);
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [containerRef]);

  return position;
};
