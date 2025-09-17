'use client';

import { Controller, useFormContext } from 'react-hook-form';

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './Select';
import { cn } from 'lib/utils';
import Text from 'components/ui/Text';

interface Option {
  label: string;
  value: string;
  description?: string;
}

interface FormSelectProps {
  name: string;
  label?: string;
  options: Option[];
  placeholder?: string;
  disabled?: boolean;
  className?: string;
}

export default function FormSelect({
  name,
  label,
  options,
  placeholder = 'Select from your saved drafts or scripts',
  disabled,
  className,
}: FormSelectProps) {
  const {
    control,
    formState: { errors },
  } = useFormContext();

  return (
    <div className="mt-[-15px] flex w-full flex-col items-start gap-2 font-figtree">
      {label && (
        <Text variant="sm" className="text-white">
          {label}
        </Text>
      )}

      <Controller
        control={control}
        name={name}
        rules={{ required: 'Please select an option' }}
        render={({ field }) => (
          <Select onValueChange={field.onChange} value={field.value} disabled={disabled}>
            <SelectTrigger
              className={cn(
                'w-full rounded-2xl bg-white/10 px-4 py-3 text-left text-white',
                disabled && 'opacity-60',
                className,
              )}
            >
              <SelectValue placeholder={placeholder} />
            </SelectTrigger>
            <SelectContent>
              {options.map((opt) => (
                <SelectItem key={opt.value} value={opt.value} description={opt.description}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}
      />

      {errors[name]?.message && (
        <Text variant="xs" className="text-rose-500">
          {errors[name]?.message?.toString()}
        </Text>
      )}
    </div>
  );
}
