'use client';

import { TextareaHTMLAttributes } from 'react';
import { RegisterOptions, useFormContext } from 'react-hook-form';

import { cn } from 'lib/utils';
import Text from 'components/ui/Text';

interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  name: string;
  label?: string;
  validationSchema?: RegisterOptions;
}

export default function FormTextArea(props: TextareaProps) {
  const {
    name,
    disabled,
    className,
    label = '',
    validationSchema = undefined,
    rows = 4,
    ...textareaProps
  } = props;

  const {
    register,
    formState: { errors },
  } = useFormContext();

  return (
    <div className="flex w-full flex-col items-start gap-2 self-stretch font-figtree">
      {label && (
        <Text variant="base" className="font-medium text-white">
          {label}
        </Text>
      )}
      <div
        className={cn('flex w-full rounded-2xl bg-white/10', disabled && 'opacity-60', className)}
      >
        <textarea
          // eslint-disable-next-line react/jsx-props-no-spreading
          {...textareaProps}
          disabled={disabled}
          rows={rows}
          {...register(name, validationSchema)}
          className="w-full resize-none rounded-2xl border-none bg-transparent p-4 text-base leading-6 tracking-[-0.2px] text-white outline-0 placeholder:text-[#737373]"
        />
      </div>
      {errors[name]?.message && (
        <Text variant="xs" className="text-rose-500">
          {errors[name]?.message?.toString()}
        </Text>
      )}
    </div>
  );
}
