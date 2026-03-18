'use client';

import { useMemo } from 'react';
import { useFormContext } from 'react-hook-form';

import { ToneType } from '../types';
import InfoModal from './InfoModal';
import { cn } from 'lib/utils';

export default function VibeToneWidget({ tones, name }: { tones: ToneType[]; name: string }) {
  const {
    register,
    watch,
    formState: { errors },
  } = useFormContext();

  const { onChange } = register(name, {
    validate: (value: number[]) => {
      if (!Array.isArray(value)) return 'Tones must be an array';
      if (value.length > 3) return 'You can only select up to 3 tones';
      return true;
    },
  });

  const selectedIds: number[] = watch(name) ?? [];

  const handleToggle = (toneId: number) => {
    const next = selectedIds.includes(toneId)
      ? selectedIds.filter((id) => id !== toneId)
      : [...selectedIds, toneId];
    onChange({ target: { name, value: next } });
  };

  const selectedTones = useMemo(
    () => tones.filter((t) => selectedIds.includes(t.id)),

    [tones, selectedIds],
  );

  return (
    <div className="flex flex-col gap-3">
      {/* Label */}
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium text-foreground">Video tone</span>
        <InfoModal description="Choose up to 3 tones that match your content style and target audience." />
        <span className="ml-auto text-xs text-muted-foreground">
          {selectedIds.length}/3 selected
        </span>
      </div>

      {/* Chip grid */}
      <div className="flex flex-wrap gap-2">
        {tones.map((tone) => {
          const active = selectedIds.includes(tone.id);
          const maxReached = selectedIds.length >= 3 && !active;

          return (
            <button
              key={tone.id}
              type="button"
              disabled={maxReached}
              onClick={() => handleToggle(tone.id)}
              className={cn(
                'rounded-md border px-3 py-1.5 text-sm font-medium transition-colors',
                active
                  ? 'border-primary bg-accent text-accent-foreground'
                  : 'border-border bg-transparent text-muted-foreground hover:border-primary/40 hover:bg-muted hover:text-foreground',
                maxReached && 'cursor-not-allowed opacity-40',
              )}
            >
              {tone.name}
            </button>
          );
        })}
      </div>

      {/* Selected summary */}
      {selectedTones.length > 0 && (
        <p className="text-xs text-muted-foreground">
          Selected: {selectedTones.map((t) => t.name).join(', ')}
        </p>
      )}

      {errors[name]?.message && (
        <p className="text-xs text-destructive">{errors[name]?.message?.toString()}</p>
      )}
    </div>
  );
}
