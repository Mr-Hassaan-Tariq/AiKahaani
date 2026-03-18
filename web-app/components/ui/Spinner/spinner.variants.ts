import { cva } from 'class-variance-authority';

export const spinnerVariants = cva(
  // ── Base styles ──────────────────────────────────────────────────
  'animate-spin rounded-full border-2 border-current border-t-transparent',
  {
    variants: {
      size: {
        sm: 'h-3 w-3',
        md: 'h-4 w-4',
        lg: 'h-6 w-6',
        xl: 'h-8 w-8',
      },
      color: {
        current: 'text-current',
        primary: 'text-primary',
        muted: 'text-muted-foreground',
        white: 'text-white',
      },
    },
    defaultVariants: {
      size: 'md',
      color: 'current',
    },
  },
);
