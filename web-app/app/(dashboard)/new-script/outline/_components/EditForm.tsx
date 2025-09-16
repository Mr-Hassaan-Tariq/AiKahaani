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
      <div className="flex items-center space-x-2">
        <span className="text-sm font-semibold text-white/90">{cardId}.</span>
        <div className="flex-1">
          <input
            ref={titleInputRef}
            type="text"
            value={editValues.title}
            onChange={(e) => onInputChange('title', e.target.value)}
            onKeyDown={onKeyDown}
            className={`w-full rounded-lg border px-3 py-2 text-white placeholder-white/50 transition-colors duration-200 focus:outline-none focus:ring-2 ${
              validationErrors.title
                ? 'border-red-400 bg-red-500/10 focus:ring-red-400/30'
                : 'border-white/20 bg-white/10 focus:border-transparent focus:ring-white/30'
            }`}
            placeholder="Enter title... *"
          />
          {validationErrors.title && <p className="mt-1 text-xs text-red-400">Title is required</p>}
        </div>
        <div className="flex space-x-1">
          <button
            onClick={onSave}
            className="rounded-full bg-green-500/20 p-1 text-green-400 transition-colors duration-200 hover:bg-green-500/30 hover:text-green-300 disabled:cursor-not-allowed disabled:opacity-50"
            title="Save (Ctrl+Enter)"
            disabled={!isFormValid}
          >
            <Check size={16} />
          </button>
          <button
            onClick={onCancel}
            className="rounded-full bg-red-500/20 p-1 text-red-400 transition-colors duration-200 hover:bg-red-500/30 hover:text-red-300"
            title="Cancel (Esc)"
          >
            <X size={16} />
          </button>
        </div>
      </div>
      <div>
        <textarea
          ref={descriptionInputRef}
          value={editValues.description}
          onChange={(e) => onInputChange('description', e.target.value)}
          onKeyDown={onKeyDown}
          className={`w-full resize-none rounded-lg border px-3 py-2 text-white placeholder-white/50 transition-colors duration-200 focus:outline-none focus:ring-2 ${
            validationErrors.description
              ? 'border-red-400 bg-red-500/10 focus:ring-red-400/30'
              : 'border-white/20 bg-white/10 focus:border-transparent focus:ring-white/30'
          }`}
          placeholder="Enter description... *"
          rows={2}
        />
        {validationErrors.description && (
          <p className="mt-1 text-xs text-red-400">Description is required</p>
        )}
      </div>
    </div>
  );
};
