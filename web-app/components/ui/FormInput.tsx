'use client';

import { InputHTMLAttributes } from 'react';
import { RegisterOptions, useFormContext } from 'react-hook-form';

import { cn } from 'lib/utils';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  name: string;
  label?: string;
  validationSchema?: RegisterOptions;
}

export default function FormInput(props: InputProps) {
  const {
    name,
    type = 'text',
    disabled,
    className,
    label = '',
    validationSchema = undefined,
    ...inputProps
  } = props;

  const {
    register,
    formState: { errors },
  } = useFormContext();

  return (
    <div className="flex w-full flex-col gap-1.5">
      {label && (
        <label htmlFor={name} className="text-sm font-medium text-foreground">
          {label}
        </label>
      )}
      <input
        id={name}
        type={type}
        disabled={disabled}
        {...inputProps}
        {...register(name, validationSchema)}
        className={cn(
          'h-10 w-full rounded-md border border-border bg-input px-3 text-sm text-foreground placeholder:text-muted-foreground',
          'focus:outline-none focus:ring-1 focus:ring-ring',
          disabled && 'cursor-not-allowed opacity-60',
          className,
        )}
      />
      {errors[name]?.message && (
        <p className="text-xs text-destructive">{errors[name]?.message?.toString()}</p>
      )}
    </div>
  );
}
