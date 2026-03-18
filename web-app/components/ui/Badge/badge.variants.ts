import { cva } from 'class-variance-authority';

export const badgeVariants = cva(
  // ── Base styles ──────────────────────────────────────────────────
  'inline-flex items-center gap-1 rounded-md font-medium whitespace-nowrap',
  {
    variants: {
      // ── Visual style ─────────────────────────────────────────────
      variant: {
        default:     'bg-secondary    text-secondary-foreground',
        primary:     'bg-accent       text-accent-foreground',
        success:     'bg-success/10   text-success',
        warning:     'bg-warning/10   text-warning-foreground',
        destructive: 'bg-destructive/10 text-destructive',
        outline:     'border border-border bg-transparent text-foreground',
        muted:       'bg-muted        text-muted-foreground',
      },

      // ── Size ─────────────────────────────────────────────────────
      size: {
        sm: 'px-2   py-0.5 text-xs',
        md: 'px-2.5 py-1   text-xs',
      },
    },
    defaultVariants: {
      variant: 'default',
      size:    'md',
    },
  },
);
