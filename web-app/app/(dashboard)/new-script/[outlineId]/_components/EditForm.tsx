import { Check, X } from 'lucide-react';

import { EditValues, ValidationErrors } from './utils';

interface EditFormProps {
  cardId: number;
  editValues: EditValues;
  validationErrors: ValidationErrors;
  titleInputRef: React.RefObject<HTMLInputElement | null>;
  descriptionInputRef: React.RefObject<HTMLTextAreaElement | null>;
  onInputChange: (field: 'title' | 'description', value: string) => void;
  onKeyDown: (e: React.KeyboardEvent) => void;
  onSave: () => void;
  onCancel: () => void;
  isFormValid: boolean;
}

export const EditForm = ({
  cardId,
  editValues,
  validationErrors,
  titleInputRef,
  descriptionInputRef,
  onInputChange,
  onKeyDown,
  onSave,
  onCancel,
  isFormValid,
}: EditFormProps) => {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <span className="shrink-0 text-xs font-semibold text-primary">
          {String(cardId).padStart(2, '0')}
        </span>
        <div className="flex-1">
          <input
            ref={titleInputRef}
            type="text"
            value={editValues.title}
            onChange={(e) => onInputChange('title', e.target.value)}
            onKeyDown={onKeyDown}
            className={`w-full rounded-lg border bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring ${
              validationErrors.title ? 'border-destructive' : 'border-border'
            }`}
            placeholder="Section title…"
          />
          {validationErrors.title && (
            <p className="mt-1 text-xs text-destructive">Title is required</p>
          )}
        </div>
        <div className="flex shrink-0 gap-1">
          <button
            onClick={onSave}
            disabled={!isFormValid}
            title="Save (Ctrl+Enter)"
            className="flex h-7 w-7 items-center justify-center rounded-full bg-success/10 text-success transition-colors hover:bg-success/20 disabled:cursor-not-allowed disabled:opacity-40"
          >
            <Check size={14} />
          </button>
          <button
            onClick={onCancel}
            title="Cancel (Esc)"
            className="flex h-7 w-7 items-center justify-center rounded-full bg-destructive/10 text-destructive transition-colors hover:bg-destructive/20"
          >
            <X size={14} />
          </button>
        </div>
      </div>

      <div>
        <textarea
          ref={descriptionInputRef}
          value={editValues.description}
          onChange={(e) => onInputChange('description', e.target.value)}
          onKeyDown={onKeyDown}
          rows={2}
          className={`w-full resize-none rounded-lg border bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring ${
            validationErrors.description ? 'border-destructive' : 'border-border'
          }`}
          placeholder="Brief description of this section…"
        />
        {validationErrors.description && (
          <p className="mt-1 text-xs text-destructive">Description is required</p>
        )}
      </div>
    </div>
  );
};
