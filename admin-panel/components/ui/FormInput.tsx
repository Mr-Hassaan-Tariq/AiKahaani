'use client';

import React from 'react';
import { RegisterOptions, useFormContext } from 'react-hook-form';

import { cn } from 'lib/utils';
import Text from 'components/ui/Text';

interface BaseProps {
  name: string;
  label?: string;
  validationSchema?: RegisterOptions;
  /**
   * Use `type="textarea"` to render a textarea.
   */
  type?: string;
  /**
   * Rows for textarea (only used when type === 'textarea')
   */
  rows?: number;
  /**
   * If you need to pass specific textarea props (e.g. wrap, maxLength),
   * provide them here. This avoids conflicting attribute types.
   */
  textareaProps?: React.TextareaHTMLAttributes<HTMLTextAreaElement>;
}

/**
 * We extend only input attributes to avoid the TypeScript conflict
 * between input and textarea attribute types. Textarea-only props can
 * be passed in `textareaProps`.
 */
type InputProps = BaseProps & Omit<React.InputHTMLAttributes<HTMLInputElement>, 'name' | 'type'>;

export default function FormInput(props: InputProps) {
  const {
    name,
    type = 'text',
    disabled,
    className,
    label = '',
    validationSchema = undefined,
    rows = 4,
    textareaProps,
    ...inputProps
  } = props;

  const {
    register,
    formState: { errors },
  } = useFormContext();

  const sharedWrapperClasses = cn(
    'flex w-full flex-col items-start gap-2 self-stretch font-figtree',
    className,
  );

  const inputContainerBase = 'flex w-full items-center justify-start rounded-2xl bg-white/10';
  const inputBaseClasses =
    'w-full rounded-2xl border-none bg-transparent p-4 text-base leading-6 tracking-[-0.2px] text-white outline-0 placeholder:text-[#737373]';

  return (
    <div className={sharedWrapperClasses}>
      {label && (
        <Text variant="base" className="font-medium text-white">
          {label}
        </Text>
      )}

      {/* Input container */}
      <div className={cn(inputContainerBase, disabled && 'opacity-60')}>
        {type === 'textarea' ? (
          // Textarea
          // register textarea with react-hook-form

          <textarea
            // register with the same name/validation
            // eslint-disable-next-line react/jsx-props-no-spreading
            {...register(name, validationSchema)}
            // spread any input-like props that still make sense for textarea
            // (we cast safely because inputProps may include things like placeholder)
            // eslint-disable-next-line react/jsx-props-no-spreading
            {...(inputProps as React.TextareaHTMLAttributes<HTMLTextAreaElement>)}
            // then apply textarea-specific props
            // eslint-disable-next-line react/jsx-props-no-spreading
            {...textareaProps}
            rows={rows}
            disabled={disabled}
            className={cn(
              inputBaseClasses,
              // allow textarea to grow without being too tall by default
              'resize-vertical min-h-[120px]',
            )}
          />
        ) : (
          // Regular input

          <input
            // eslint-disable-next-line react/jsx-props-no-spreading
            {...(inputProps as React.InputHTMLAttributes<HTMLInputElement>)}
            disabled={disabled}
            type={type}
            // eslint-disable-next-line react/jsx-props-no-spreading
            {...register(name, validationSchema)}
            className={cn(inputBaseClasses, 'h-[57px]')}
          />
        )}
      </div>

      {/* Validation error */}
      {errors[name]?.message && (
        <Text variant="xs" className="text-rose-500">
          {errors[name]?.message?.toString()}
        </Text>
      )}
    </div>
  );
}
