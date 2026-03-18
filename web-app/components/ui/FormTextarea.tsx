import { TextareaHTMLAttributes, ReactNode } from 'react';
import { RegisterOptions, useFormContext } from 'react-hook-form';

import { cn } from 'lib/utils';

type FormTextareaProps = TextareaHTMLAttributes<HTMLTextAreaElement> & {
  label?: ReactNode;
  name: string;
  validationSchema?: RegisterOptions;
};

export default function FormTextarea({
  label,
  name,
  validationSchema,
  className,
  ...props
}: FormTextareaProps) {
  const {
    register,
    formState: { errors },
  } = useFormContext();

  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label className="text-sm font-medium text-foreground">{label}</label>
      )}
      <textarea
        {...props}
        {...register(name, validationSchema)}
        className={cn(
          'min-h-[120px] w-full resize-none rounded-lg border border-border bg-input px-4 py-3',
          'text-sm text-foreground placeholder:text-muted-foreground',
          'focus:outline-none focus:ring-2 focus:ring-ring',
          'transition-colors disabled:cursor-not-allowed disabled:opacity-50',
          errors[name] && 'border-destructive focus:ring-destructive',
          className,
        )}
      />
      {errors[name]?.message && (
        <p className="text-xs text-destructive">{errors[name]?.message?.toString()}</p>
      )}
    </div>
  );
}
