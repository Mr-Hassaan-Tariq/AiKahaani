import { cva } from 'class-variance-authority';

export const buttonVariants = cva(
  // ── Base styles ──────────────────────────────────────────────────
  'inline-flex items-center justify-center font-medium whitespace-nowrap transition-colors ' +
  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1 ' +
  'disabled:pointer-events-none disabled:opacity-50 cursor-pointer select-none',
  {
    variants: {
      // ── Visual style ─────────────────────────────────────────────
      variant: {
        primary:     'bg-primary text-primary-foreground hover:bg-primary/90',
        secondary:   'bg-secondary text-secondary-foreground hover:bg-secondary/70',
        outline:     'border border-border bg-transparent text-foreground hover:bg-muted',
        ghost:       'bg-transparent text-muted-foreground hover:bg-muted hover:text-foreground',
        destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
        link:        'bg-transparent text-primary underline-offset-4 hover:underline p-0 h-auto',
      },

      // ── Size ─────────────────────────────────────────────────────
      size: {
        sm:   'h-8  px-3   text-xs  rounded-md  gap-1.5',
        md:   'h-10 px-4   text-sm  rounded-lg  gap-2',
        lg:   'h-12 px-6   text-sm  rounded-lg  gap-2',
        icon: 'h-9  w-9            rounded-lg',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size:    'md',
    },
  },
);
