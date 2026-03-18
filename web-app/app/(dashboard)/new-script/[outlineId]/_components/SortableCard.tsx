import { Trash2 } from 'lucide-react';

import { CardView } from './CardView';
import DeleteOutlineSection from './DeleteOutlineSection';
import { DragHandle } from './DragHandle';
import { EditForm } from './EditForm';
import { CardData, isFormValid } from './utils';
import { cn } from 'lib/utils';

interface SortableCardProps {
  card: CardData;
  index: number;
  isEditing: boolean;
  editValues: { title: string; description: string };
  validationErrors: { title: boolean; description: boolean };
  isDragged: boolean;
  isDragOver: boolean;
  showDropIndicator: boolean;
  titleInputRef: React.RefObject<HTMLInputElement | null>;
  descriptionInputRef: React.RefObject<HTMLTextAreaElement | null>;
  onDragStart: (e: React.DragEvent) => void;
  onDragOver: (e: React.DragEvent) => void;
  onDragLeave: () => void;
  onDrop: (e: React.DragEvent) => void;
  onDragEnd: () => void;
  onEdit: (card: CardData) => void;
  onInputChange: (field: 'title' | 'description', value: string) => void;
  onKeyDown: (e: React.KeyboardEvent) => void;
  onSave: () => void;
  onCancel: () => void;
  onDelete: (id: number) => void;
  onTouchStart?: (e: React.TouchEvent) => void;
  onTouchMove?: (e: React.TouchEvent) => void;
  onTouchEnd?: () => void;
}

export const SortableCard = ({
  card,
  isEditing,
  editValues,
  validationErrors,
  isDragged,
  isDragOver,
  showDropIndicator,
  titleInputRef,
  descriptionInputRef,
  onDragStart,
  onDragOver,
  onDragLeave,
  onDrop,
  onDragEnd,
  onEdit,
  onInputChange,
  onKeyDown,
  onSave,
  onCancel,
  onDelete,
  onTouchStart,
  onTouchMove,
  onTouchEnd,
}: SortableCardProps) => {
  return (
    <div className="relative">
      {/* Drop indicator */}
      {showDropIndicator && (
        <div className="absolute -bottom-1.5 left-0 right-0 z-10 h-0.5 rounded-full bg-primary" />
      )}

      <div
        className={cn(
          'group relative flex flex-row items-center rounded-xl border border-border bg-card transition-all',
          isDragged && 'scale-[0.98] opacity-40 shadow-lg',
          isDragOver && 'border-primary/40 bg-accent',
        )}
        onDragOver={(e) => onDragOver(e)}
        onDragLeave={onDragLeave}
        onDrop={(e) => onDrop(e)}
        onDragEnd={onDragEnd}
      >
        {/* Drag Handle */}
        <DragHandle
          isEditing={isEditing}
          onDragStart={(e) => onDragStart(e)}
          onDragOver={(e) => onDragOver(e)}
          onDragLeave={onDragLeave}
          onDrop={(e) => onDrop(e)}
          onDragEnd={onDragEnd}
          onTouchStart={onTouchStart}
          onTouchMove={onTouchMove}
          onTouchEnd={onTouchEnd}
        />

        {/* Content */}
        <div className="ml-8 flex-1 py-4 pr-4">
          {isEditing ? (
            <EditForm
              cardId={card.id}
              editValues={editValues}
              validationErrors={validationErrors}
              titleInputRef={titleInputRef}
              descriptionInputRef={descriptionInputRef}
              onInputChange={onInputChange}
              onKeyDown={onKeyDown}
              onSave={onSave}
              onCancel={onCancel}
              isFormValid={isFormValid(editValues)}
            />
          ) : (
            <CardView card={card} onEdit={onEdit} />
          )}
        </div>

        {/* Delete Button */}
        <DeleteOutlineSection
          onDelete={() => onDelete(card.id)}
          trigger={
            <div className="mr-3 flex h-8 w-8 shrink-0 cursor-pointer items-center justify-center rounded-lg text-muted-foreground opacity-0 transition-all hover:bg-destructive/10 hover:text-destructive group-hover:opacity-100">
              <Trash2 size={15} />
            </div>
          }
        />
      </div>
    </div>
  );
};
