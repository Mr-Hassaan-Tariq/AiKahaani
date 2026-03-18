import { cva } from 'class-variance-authority';

export const inputVariants = cva(
  // ── Base styles ──────────────────────────────────────────────────
  'w-full rounded-lg border bg-input px-3 text-sm text-foreground ' +
    'placeholder:text-muted-foreground ' +
    'focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-0 ' +
    'transition-colors disabled:cursor-not-allowed disabled:opacity-50',
  {
    variants: {
      // ── Size ─────────────────────────────────────────────────────
      size: {
        sm: 'h-8  text-xs',
        md: 'h-10',
        lg: 'h-12 text-base',
      },

      // ── Validation state ─────────────────────────────────────────
      state: {
        default: 'border-border',
        error: 'border-destructive focus:ring-destructive',
        success: 'border-success    focus:ring-success',
      },
    },
    defaultVariants: {
      size: 'md',
      state: 'default',
    },
  },
);
