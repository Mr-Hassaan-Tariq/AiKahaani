import * as React from 'react';
import { type VariantProps } from 'class-variance-authority';

import { spinnerVariants } from './spinner.variants';
import { cn } from 'lib/utils';

export interface SpinnerProps
  extends Omit<React.HTMLAttributes<HTMLSpanElement>, 'color'>,
    VariantProps<typeof spinnerVariants> {
  /** Accessible label for screen readers */
  label?: string;
}

const Spinner = React.forwardRef<HTMLSpanElement, SpinnerProps>(
  ({ className, size, color, label = 'Loading…', ...props }, ref) => (
    <span
      ref={ref}
      role="status"
      aria-label={label}
      className={cn(spinnerVariants({ size, color }), className)}
      {...props}
    />
  ),
);

Spinner.displayName = 'Spinner';

// ── PageSpinner — full-screen centered overlay ───────────────────────
export function PageSpinner() {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
      <Spinner size="xl" color="primary" label="Loading page…" />
    </div>
  );
}

export { Spinner, spinnerVariants };
export default Spinner;
