'use client';

import * as React from 'react';
import * as SliderPrimitive from '@radix-ui/react-slider';

import { cn } from 'lib/utils';

const Slider = React.forwardRef<
  React.ElementRef<typeof SliderPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof SliderPrimitive.Root>
>(({ className, disabled, ...props }, ref) => (
  <SliderPrimitive.Root
    ref={ref}
    disabled={disabled}
    className={cn(
      'relative flex w-full touch-none select-none items-center bg-transparent',
      disabled && 'opacity-30',
      className,
    )}
    {...props}
  >
    <SliderPrimitive.Track className="relative flex h-2 w-full grow items-center rounded-full bg-secondary">
      <SliderPrimitive.Range className="absolute h-full rounded-full bg-primary" />
    </SliderPrimitive.Track>
    <SliderPrimitive.Thumb className="block h-5 w-5 rounded-full bg-primary ring-4 ring-primary/20 transition-colors focus-visible:outline-none focus-visible:ring-primary/30 disabled:pointer-events-none disabled:opacity-50" />
    {Number(props.defaultValue?.length) > 1 && (
      <SliderPrimitive.Thumb className="block h-5 w-5 rounded-full bg-primary ring-4 ring-primary/20 transition-colors focus-visible:outline-none focus-visible:ring-primary/30 disabled:pointer-events-none disabled:opacity-50" />
    )}
  </SliderPrimitive.Root>
));
Slider.displayName = SliderPrimitive.Root.displayName;

export { Slider };
