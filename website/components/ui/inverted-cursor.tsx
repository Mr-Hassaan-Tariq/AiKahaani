'use client';

import React, { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';

import { cn } from 'lib/utils';

interface CursorProps {
  size?: number;
  variant?: 'default' | 'red';
  className?: string;
}

export const Cursor: React.FC<CursorProps> = ({ size = 60, variant = 'red', className }) => {
  const cursorRef = useRef<HTMLDivElement>(null);
  const requestRef = useRef<number | undefined>(undefined);
  const posRef = useRef({ x: 0, y: 0 });
  const targetRef = useRef({ x: 0, y: 0 });

  const [visible, setVisible] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted) return;

    const handleMouseMove = (e: MouseEvent) => {
      setVisible(true);
      targetRef.current = { x: e.clientX, y: e.clientY };
    };

    const animate = () => {
      if (!cursorRef.current) {
        requestRef.current = requestAnimationFrame(animate);
        return;
      }

      const { x: tx, y: ty } = targetRef.current;
      const { x: cx, y: cy } = posRef.current;

      const newX = cx + (tx - cx) * 0.25;
      const newY = cy + (ty - cy) * 0.25;

      posRef.current = { x: newX, y: newY };
      cursorRef.current.style.transform = `translate(${newX}px, ${newY}px) translate(-50%, -50%)`;

      requestRef.current = requestAnimationFrame(animate);
    };

    window.addEventListener('mousemove', handleMouseMove);
    requestRef.current = requestAnimationFrame(animate);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      if (requestRef.current) cancelAnimationFrame(requestRef.current);
    };
  }, [mounted]);

  if (!mounted || typeof document === 'undefined') return null;

  const cursorEl = (
    <div
      className={cn(
        'pointer-events-none fixed inset-0 isolate cursor-none',
        '[transform:translateZ(0)]',
        className
      )}
      style={{ zIndex: 2147483647 }}
      aria-hidden="true"
    >
      <div
        ref={cursorRef}
        className={cn(
          'absolute left-0 top-0 rounded-full transition-opacity duration-200',
          variant === 'red'
            ? 'border-2 border-red-500 bg-red-500/40 dark:border-red-400 dark:bg-red-500/50'
            : 'bg-white mix-blend-difference'
        )}
        style={{
          width: size,
          height: size,
          opacity: visible ? 1 : 0,
        }}
      />
    </div>
  );

  return createPortal(cursorEl, document.body);
};

export default Cursor;
