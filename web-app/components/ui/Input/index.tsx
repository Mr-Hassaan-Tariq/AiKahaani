import * as React from 'react';
import { type VariantProps } from 'class-variance-authority';

import { cn } from 'lib/utils';
import { inputVariants } from './input.variants';

export interface InputProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'>,
    VariantProps<typeof inputVariants> {
  /** Label rendered above the input */
  label?: string;
  /** Error message rendered below the input */
  error?: string;
  /** Helper text rendered below the input (shown when no error) */
  hint?: string;
  /** Icon or element shown on the left inside the input */
  leftSlot?: React.ReactNode;
  /** Icon or element shown on the right inside the input */
  rightSlot?: React.ReactNode;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, hint, size, state, leftSlot, rightSlot, id, ...props }, ref) => {
    const inputId = id ?? label?.toLowerCase().replace(/\s+/g, '-');
    const resolvedState = error ? 'error' : state;

    return (
      <div className="flex flex-col gap-1.5 w-full">
        {label && (
          <label
            htmlFor={inputId}
            className="text-sm font-medium text-foreground"
          >
            {label}
          </label>
        )}

        <div className="relative flex items-center">
          {leftSlot && (
            <span className="absolute left-3 flex items-center text-muted-foreground">
              {leftSlot}
            </span>
          )}

          <input
            ref={ref}
            id={inputId}
            className={cn(
              inputVariants({ size, state: resolvedState }),
              leftSlot  && 'pl-9',
              rightSlot && 'pr-9',
              className,
            )}
            {...props}
          />

          {rightSlot && (
            <span className="absolute right-3 flex items-center text-muted-foreground">
              {rightSlot}
            </span>
          )}
        </div>

        {error && (
          <p className="text-xs text-destructive">{error}</p>
        )}
        {!error && hint && (
          <p className="text-xs text-muted-foreground">{hint}</p>
        )}
      </div>
    );
  },
);

Input.displayName = 'Input';

export { Input, inputVariants };
export default Input;
