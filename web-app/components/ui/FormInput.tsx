'use client';

import { InputHTMLAttributes } from 'react';
import { RegisterOptions, useFormContext } from 'react-hook-form';

import { cn } from 'lib/utils';
import Text from 'components/ui/Text';

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
    <div className="flex w-full flex-col items-start gap-2 self-stretch font-figtree">
      {label && (
        <Text variant="base" className="font-medium text-white">
          {label}
        </Text>
      )}
      <div
        className={cn(
          'flex h-[57px] w-full items-center justify-start rounded-2xl bg-white/10',
          disabled && 'opacity-60',
          className,
        )}
      >
        <input
          // eslint-disable-next-line react/jsx-props-no-spreading
          {...inputProps}
          type={type}
          // eslint-disable-next-line react/jsx-props-no-spreading
          {...register(name, validationSchema)}
          className="h-full w-full rounded-2xl border-none bg-transparent p-4 text-base leading-6 tracking-[-0.2px] text-white outline-0 placeholder:text-[#737373]"
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
