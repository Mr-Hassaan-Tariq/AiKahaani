'use client';

import { memo, useCallback, useEffect, useRef } from 'react';
import { animate } from 'motion/react';

import { cn } from 'lib/utils';

interface GlowingEffectProps {
  blur?: number;
  inactiveZone?: number;
  proximity?: number;
  spread?: number;
  variant?: 'default' | 'white' | 'blue-purple' | 'red';
  glow?: boolean;
  className?: string;
  disabled?: boolean;
  movementDuration?: number;
  borderWidth?: number;
}

const gradients = {
  default: `radial-gradient(circle, #dd7bbb 10%, #dd7bbb00 20%),
            radial-gradient(circle at 40% 40%, #d79f1e 5%, #d79f1e00 15%),
            radial-gradient(circle at 60% 60%, #5a922c 10%, #5a922c00 20%),
            radial-gradient(circle at 40% 60%, #4c7894 10%, #4c789400 20%),
            repeating-conic-gradient(
              from 236.84deg at 50% 50%,
              #dd7bbb 0%,
              #d79f1e calc(25% / var(--repeating-conic-gradient-times)),
              #5a922c calc(50% / var(--repeating-conic-gradient-times)),
              #4c7894 calc(75% / var(--repeating-conic-gradient-times)),
              #dd7bbb calc(100% / var(--repeating-conic-gradient-times))
            )`,
  white: `repeating-conic-gradient(
            from 236.84deg at 50% 50%,
            #000,
            #000 calc(25% / var(--repeating-conic-gradient-times))
          )`,
  'blue-purple': `radial-gradient(circle at 25% 25%, rgba(59, 130, 246, 0.4) 0%, transparent 30%),
                  radial-gradient(circle at 75% 25%, rgba(147, 51, 234, 0.3) 0%, transparent 30%),
                  radial-gradient(circle at 25% 75%, rgba(168, 85, 247, 0.3) 0%, transparent 30%),
                  radial-gradient(circle at 75% 75%, rgba(99, 102, 241, 0.4) 0%, transparent 30%),
                  repeating-conic-gradient(
                    from calc(var(--start) * 1deg) at 50% 50%,
                    rgba(59, 130, 246, 0.9) 0%,
                    rgba(147, 51, 234, 1) calc(25% / var(--repeating-conic-gradient-times)),
                    rgba(168, 85, 247, 0.95) calc(50% / var(--repeating-conic-gradient-times)),
                    rgba(99, 102, 241, 0.9) calc(75% / var(--repeating-conic-gradient-times)),
                    rgba(59, 130, 246, 0.9) calc(100% / var(--repeating-conic-gradient-times))
                  )`,
  red: `radial-gradient(circle at 25% 25%, rgba(220, 38, 38, 0.4) 0%, transparent 30%),
        radial-gradient(circle at 75% 25%, rgba(236, 72, 153, 0.3) 0%, transparent 30%),
        radial-gradient(circle at 25% 75%, rgba(244, 63, 94, 0.3) 0%, transparent 30%),
        radial-gradient(circle at 75% 75%, rgba(239, 68, 68, 0.4) 0%, transparent 30%),
        repeating-conic-gradient(
          from calc(var(--start) * 1deg) at 50% 50%,
          rgba(220, 38, 38, 0.9) 0%,
          rgba(236, 72, 153, 1) calc(25% / var(--repeating-conic-gradient-times)),
          rgba(244, 63, 94, 0.95) calc(50% / var(--repeating-conic-gradient-times)),
          rgba(239, 68, 68, 0.9) calc(75% / var(--repeating-conic-gradient-times)),
          rgba(220, 38, 38, 0.9) calc(100% / var(--repeating-conic-gradient-times))
        )`,
};

export const GlowingEffect = memo(
  ({
    blur = 0,
    inactiveZone = 0.7,
    proximity = 0,
    spread = 25,
    variant = 'red',
    glow = false,
    className,
    movementDuration = 1,
    borderWidth = 2,
    disabled = true,
  }: GlowingEffectProps) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const lastPosition = useRef({ x: 0, y: 0 });
    const animationFrameRef = useRef<number>(0);

    const handleMove = useCallback(
      (e?: MouseEvent | PointerEvent | { x: number; y: number }) => {
        if (!containerRef.current) return;

        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current);
        }

        animationFrameRef.current = requestAnimationFrame(() => {
          const element = containerRef.current;
          if (!element) return;

          const { left, top, width, height } = element.getBoundingClientRect();
          let mouseX: number;
          let mouseY: number;
          if (e && 'clientX' in e) {
            mouseX = (e as MouseEvent).clientX;
            mouseY = (e as MouseEvent).clientY;
            lastPosition.current = { x: mouseX, y: mouseY };
          } else if (e && 'x' in e) {
            mouseX = (e as { x: number; y: number }).x;
            mouseY = (e as { x: number; y: number }).y;
            lastPosition.current = { x: mouseX, y: mouseY };
          } else {
            mouseX = lastPosition.current.x;
            mouseY = lastPosition.current.y;
          }

          const centerX = left + width / 2;
          const centerY = top + height / 2;
          const distanceFromCenter = Math.hypot(mouseX - centerX, mouseY - centerY);
          const inactiveRadius = 0.5 * Math.min(width, height) * inactiveZone;

          if (distanceFromCenter < inactiveRadius) {
            element.style.setProperty('--active', '0');
            return;
          }

          const isActive =
            mouseX > left - proximity &&
            mouseX < left + width + proximity &&
            mouseY > top - proximity &&
            mouseY < top + height + proximity;

          element.style.setProperty('--active', isActive ? '1' : '0');

          if (!isActive) return;

          const currentAngle = parseFloat(element.style.getPropertyValue('--start')) || 0;
          const targetAngle = (180 * Math.atan2(mouseY - centerY, mouseX - centerX)) / Math.PI + 90;

          const angleDiff = ((targetAngle - currentAngle + 180) % 360) - 180;
          const newAngle = currentAngle + angleDiff;

          animate(currentAngle, newAngle, {
            duration: movementDuration,
            ease: [0.16, 1, 0.3, 1],
            onUpdate: (value) => {
              element.style.setProperty('--start', String(value));
            },
          });
        });
      },
      [inactiveZone, proximity, movementDuration]
    );

    useEffect(() => {
      if (disabled) return;

      const handleScroll = () => handleMove();
      const handlePointerMove = (e: PointerEvent) => handleMove(e);

      window.addEventListener('scroll', handleScroll, { passive: true });
      document.body.addEventListener('pointermove', handlePointerMove, { passive: true });

      return () => {
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current);
        }
        window.removeEventListener('scroll', handleScroll);
        document.body.removeEventListener('pointermove', handlePointerMove);
      };
    }, [handleMove, disabled]);

    return (
      <>
        <div
          className={cn(
            'pointer-events-none absolute -inset-px hidden rounded-[inherit] border opacity-0 transition-opacity duration-500',
            glow && 'opacity-100',
            variant === 'white' && 'border-white',
            variant === 'blue-purple' && 'border-blue-400/30',
            variant === 'red' && 'border-red-500/30',
            disabled && '!block'
          )}
        />
        <div
          ref={containerRef}
          style={
            {
              '--blur': `${blur}px`,
              '--spread': spread,
              '--start': '0',
              '--active': '0',
              '--glowingeffect-border-width': `${borderWidth}px`,
              '--repeating-conic-gradient-times': '4',
              '--gradient': gradients[variant] ?? gradients.default,
            } as React.CSSProperties
          }
          className={cn(
            'pointer-events-none absolute inset-0 rounded-[inherit] opacity-100 transition-opacity duration-500',
            glow && 'opacity-100',
            blur > 0 && 'blur-[var(--blur)]',
            className,
            disabled && '!hidden'
          )}
        >
          <div
            className={cn(
              'glow h-full w-full rounded-[inherit]',
              'after:absolute after:inset-[calc(-1*var(--glowingeffect-border-width))] after:rounded-[inherit] after:content-[""]',
              'after:[border:var(--glowingeffect-border-width)_solid_transparent]',
              'after:[background-attachment:fixed] after:[background:var(--gradient)]',
              'after:opacity-[var(--active)] after:transition-opacity after:duration-500 after:ease-out',
              'after:[mask-clip:padding-box,border-box]',
              'after:[mask-composite:intersect]',
              'after:[mask-image:linear-gradient(#0000,#0000),conic-gradient(from_calc((var(--start)-var(--spread))*1deg),#00000000_0deg,#fff_calc(var(--spread)*0.8deg),#fff_calc(var(--spread)*1.2deg),#00000000_calc(var(--spread)*2deg))]',
              (variant === 'blue-purple' || variant === 'red') && [
                'before:absolute before:inset-0 before:rounded-[inherit] before:content-[""]',
                variant === 'blue-purple' &&
                  'before:bg-gradient-to-r before:from-blue-500/10 before:via-purple-500/10 before:to-indigo-500/10',
                variant === 'red' &&
                  'before:bg-gradient-to-r before:from-red-500/10 before:via-pink-500/10 before:to-red-600/10',
                'before:opacity-[calc(var(--active)*0.3)] before:transition-opacity before:duration-500',
                'before:-z-10 before:blur-xl',
              ]
            )}
          />
        </div>
      </>
    );
  }
);

GlowingEffect.displayName = 'GlowingEffect';
