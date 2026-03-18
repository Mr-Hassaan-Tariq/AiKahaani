import * as React from 'react';
import { type VariantProps } from 'class-variance-authority';

import { badgeVariants } from './badge.variants';
import { cn } from 'lib/utils';

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

const Badge = React.forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className, variant, size, ...props }, ref) => (
    <span ref={ref} className={cn(badgeVariants({ variant, size }), className)} {...props} />
  ),
);

Badge.displayName = 'Badge';

export { Badge, badgeVariants };
export default Badge;
