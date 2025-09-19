import { useRef, useState } from 'react';

export const useMobileDrag = () => {
  const [isDragging, setIsDragging] = useState(false);
  const [dragStartY, setDragStartY] = useState(0);
  const [dragOffset, setDragOffset] = useState(0);
  const dragRef = useRef<HTMLDivElement>(null);

  const handleTouchStart = (e: React.TouchEvent) => {
    setIsDragging(true);
    setDragStartY(e.touches[0].clientY);
    setDragOffset(0);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (!isDragging) return;

    e.preventDefault();
    const currentY = e.touches[0].clientY;
    const offset = currentY - dragStartY;
    setDragOffset(offset);
  };

  const handleTouchEnd = () => {
    setIsDragging(false);
    setDragOffset(0);
  };

  return {
    isDragging,
    dragOffset,
    dragRef,
    handleTouchStart,
    handleTouchMove,
    handleTouchEnd,
  };
};
