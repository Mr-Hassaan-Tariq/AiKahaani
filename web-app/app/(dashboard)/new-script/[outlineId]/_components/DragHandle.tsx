import { GripVertical } from 'lucide-react';

interface DragHandleProps {
  isEditing: boolean;
  onDragStart: (e: React.DragEvent) => void;
  onDragOver: (e: React.DragEvent) => void;
  onDragLeave: () => void;
  onDrop: (e: React.DragEvent) => void;
  onDragEnd: () => void;
  onTouchStart?: (e: React.TouchEvent) => void;
  onTouchMove?: (e: React.TouchEvent) => void;
  onTouchEnd?: () => void;
}

export const DragHandle = ({
  isEditing,
  onDragStart,
  onDragOver,
  onDragLeave,
  onDrop,
  onDragEnd,
  onTouchStart,
  onTouchMove,
  onTouchEnd,
}: DragHandleProps) => {
  return (
    <div
      draggable={!isEditing}
      onDragStart={onDragStart}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
      onDragEnd={onDragEnd}
      onTouchStart={onTouchStart}
      onTouchMove={onTouchMove}
      onTouchEnd={onTouchEnd}
      className="absolute left-0 top-0 flex h-full w-8 cursor-grab touch-manipulation items-center justify-center rounded-l-2xl bg-white/10 text-white/70 transition-colors duration-200 hover:bg-white/20 hover:text-white active:cursor-grabbing"
    >
      <GripVertical size={16} />
    </div>
  );
};
