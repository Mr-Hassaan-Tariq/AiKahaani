import { HTMLAttributes, ReactNode } from 'react';

import Col from './Col';
import Text from './Text';
import { cn } from 'lib/utils';

type FormTextareaProps = HTMLAttributes<HTMLTextAreaElement> & {
  label?: ReactNode;
};

export default function FormTextarea({ label, className, ...props }: FormTextareaProps) {
  return (
    <Col className="gap-2">
      {label && (
        <Text variant="base" className="font-medium text-white">
          {label}
        </Text>
      )}
      <textarea
        // eslint-disable-next-line react/jsx-props-no-spreading
        {...props}
        placeholder="e.g. Top 5 productivity hacks that actually work..."
        className={cn(
          'h-32 w-full resize-none rounded-2xl border-none bg-white/10 p-4 text-base font-medium leading-6 tracking-[-0.2px] text-white outline-none placeholder:text-brand-secondary',
          className,
        )}
      />
    </Col>
  );
}
