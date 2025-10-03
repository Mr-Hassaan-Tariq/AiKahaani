import { Trash2 } from 'lucide-react';

import { CardView } from './CardView';
import DeleteOutlineSection from './DeleteOutlineSection';
import { DragHandle } from './DragHandle';
// import { EditForm } from './EditForm';
import { CardData } from './utils';
import Card from 'components/ui/Card';

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
  // editValues,
  // validationErrors,
  isDragged,
  isDragOver,
  showDropIndicator,
  // titleInputRef,
  // descriptionInputRef,
  onDragStart,
  onDragOver,
  onDragLeave,
  onDrop,
  onDragEnd,
  onEdit,
  onDelete,
  onTouchStart,
  onTouchMove,
  onTouchEnd,
}: SortableCardProps) => {
  return (
    <div className="relative">
      {/* Drop indicator */}
      {showDropIndicator && (
        <div className="absolute -bottom-2 left-0 right-0 z-10 h-1 animate-pulse rounded-full bg-blue-400" />
      )}

      <Card
        className={`group relative flex flex-row items-center border border-white/20 bg-white/10 backdrop-blur-sm transition-all duration-200 hover:bg-white/15 hover:shadow-lg hover:shadow-white/10 ${
          isDragged ? 'scale-95 opacity-30 shadow-2xl' : ''
        } ${isDragOver ? 'bg-blue-500/10 ring-2 ring-blue-400/50' : ''}`}
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
        <div className="ml-8 w-full py-4 pr-4">
          {/* {isEditing ? (
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
          ) : ( */}
          <CardView card={card} onEdit={onEdit} />
          {/* )} */}
        </div>

        {/* Delete Button */}
        <DeleteOutlineSection
          onDelete={() => onDelete(card.id)}
          trigger={
            <div className="flex size-12 min-w-12 cursor-pointer items-center justify-center rounded-full bg-red-500/10 text-red-400 opacity-70 transition-all duration-200 hover:bg-red-500/20 hover:text-red-300 active:scale-95 group-hover:opacity-100">
              <Trash2 size={18} />
            </div>
          }
        />
      </Card>
    </div>
  );
};
