import { cva } from 'class-variance-authority';

export const cardVariants = cva(
  // ── Base styles ──────────────────────────────────────────────────
  'bg-card text-card-foreground rounded-xl',
  {
    variants: {
      // ── Visual style ─────────────────────────────────────────────
      variant: {
        default: 'border border-border shadow-sm',
        flat: 'border border-border',
        ghost: '',
        elevated: 'shadow-md',
      },

      // ── Padding ──────────────────────────────────────────────────
      padding: {
        none: '',
        sm: 'p-4',
        md: 'p-6',
        lg: 'p-8',
      },
    },
    defaultVariants: {
      variant: 'default',
      padding: 'md',
    },
  },
);
