'use client';

import { useEffect, useState } from 'react';
import { RegisterOptions, useFormContext } from 'react-hook-form';

import { LengthRangeType } from '../types';
import InfoModal from './InfoModal';
import { Slider } from 'components/shadcn_ui/slider';

const MIN_LENGTH = 'min_length';
const MAX_LENGTH = 'max_length';

export default function SliderWidget({
  range,
  disabled,
  validationSchema,
  defaultValue,
}: {
  range: LengthRangeType;
  disabled: boolean;
  validationSchema?: RegisterOptions;
  defaultValue?: number[];
}) {
  const initialValue = defaultValue ?? [range.min, range.default];
  const [wordCount, setWordCount] = useState(initialValue);

  const {
    register,
    formState: { errors },
  } = useFormContext();

  const { onChange: onMinLength } = register(MIN_LENGTH);
  const { onChange: onMaxLength } = register(MAX_LENGTH, validationSchema);

  useEffect(() => {
    onMinLength({ target: { name: MIN_LENGTH, value: wordCount[0] } });
    onMaxLength({ target: { name: MAX_LENGTH, value: wordCount[1] } });
  }, [onMinLength, onMaxLength, wordCount]);

  // approx 150 words = 1 minute
  const minMins = Math.round(wordCount[0] / 150);
  const maxMins = Math.round(wordCount[1] / 150);

  return (
    <div className={`flex flex-col gap-4 ${disabled ? 'opacity-40 pointer-events-none' : ''}`}>
      {/* Label */}
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium text-foreground">Script length</span>
        <InfoModal description="Approx. 150 words ≈ 1 minute of speech." />
        {disabled && (
          <span className="ml-auto text-xs text-muted-foreground">Disabled — using template</span>
        )}
      </div>

      {/* Slider */}
      <Slider
        defaultValue={initialValue}
        onValueChange={setWordCount}
        min={range.min}
        max={range.max}
        step={10}
        disabled={disabled}
      />

      {/* Range labels */}
      <div className="flex justify-between">
        <span className="text-xs text-muted-foreground">
          {wordCount[0].toLocaleString()} words (~{minMins}m)
        </span>
        <span className="text-xs text-muted-foreground">
          {wordCount[1].toLocaleString()} words (~{maxMins}m)
        </span>
      </div>

      {errors[MAX_LENGTH]?.message && (
        <p className="text-xs text-destructive">{errors[MAX_LENGTH]?.message?.toString()}</p>
      )}
    </div>
  );
}
