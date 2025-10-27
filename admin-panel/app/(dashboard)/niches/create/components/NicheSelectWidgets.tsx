import { useMemo, useState } from 'react';
import { ChevronDown, X } from 'lucide-react';
import { ControllerRenderProps, FieldPath, FieldValues, useFormContext } from 'react-hook-form';

import { cn } from 'lib/utils';
import Col from 'components/ui/Col';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';
import { Popover, PopoverContent, PopoverTrigger } from 'components/shadcn_ui/popover';

type OptionType = {
  value: string;
  label: string;
};

type NicheSelectWidgetProps<FormFields extends FieldValues> = {
  options: OptionType[];
  name: FieldPath<FormFields>;
  label: string;
  field: ControllerRenderProps<FormFields, FieldPath<FormFields>>;
};

export default function NicheSelectWidget<FormFields extends FieldValues>({
  options,
  name,
  label,
  field,
}: NicheSelectWidgetProps<FormFields>) {
  const [open, setOpen] = useState(false);

  const {
    watch,
    formState: { errors },
  } = useFormContext();

  const currentValues: string[] = (watch(name) as unknown as string[]) || [];

  const handleOptionToggle = (optionValue: string) => {
    const prev: string[] = currentValues || [];
    const newValues = prev.includes(optionValue)
      ? prev.filter((val) => val !== optionValue)
      : [...prev, optionValue];

    field.onChange(newValues);
  };

  const selectedOptions = useMemo(() => {
    return options.filter((option) => currentValues?.includes(option.value));
  }, [options, currentValues]);

  const selectedDisplay = useMemo(() => {
    if (selectedOptions.length === 0) {
      return `Select ${label.toLowerCase()}s`;
    }
    return selectedOptions.map((o) => o.label).join(', ');
  }, [selectedOptions, label]);

  return (
    <Col className="gap-2">
      <Text variant="base" className="font-medium text-white">
        <Row className="justify-normal gap-2">
          <span>{label}</span>
        </Row>
      </Text>

      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger
          asChild
          className="focus-visible:ring-2 focus-visible:ring-white/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#2D2D2D] data-[state=open]:border data-[state=open]:border-[#BAFF38]/[12%]"
        >
          <div className="flex h-12 w-full cursor-pointer items-center justify-between rounded-xl border border-white/10 bg-white/5 px-4 text-brand-secondary transition-colors duration-200 hover:bg-white/[0.07] focus:outline-none">
            <span
              className={cn(
                'truncate text-left text-sm font-medium', // Use truncate to handle long strings
                selectedOptions.length > 0 ? 'text-white' : 'text-[#AAACA6]', // Change text color when selected
              )}
            >
              {selectedDisplay} {/* 👈 UPDATED to show selected labels */}
            </span>
            <ChevronDown size={20} className="text-white/70" />
          </div>
        </PopoverTrigger>

        {/* Selected Tags Display (Kept this row below the trigger for quick removal/visibility) */}
        <Row className="mt-1 flex-wrap justify-normal gap-2">
          {selectedOptions?.map((option) => (
            <Row
              key={option.value}
              className="group cursor-pointer items-center rounded-full px-3 py-1 text-xs text-white transition-colors duration-200 hover:bg-red-500 hover:text-white"
              onClick={() => handleOptionToggle(option.value)}
            >
              <Text variant="sm" className="font-medium text-white group-hover:text-white">
                {option.label}
              </Text>
              <X size={12} className="ml-1" />
            </Row>
          ))}
        </Row>

        <PopoverContent
          className="w-[var(--radix-popover-trigger-width)] rounded-xl border border-[#BAFF38]/[12%] bg-[#262724] p-0 shadow-lg"
          align="start"
        >
          {options.map((option) => {
            const isSelected = selectedOptions.some((selected) => selected.value === option.value);
            return (
              <div
                key={option.value}
                className={cn(
                  'flex w-full cursor-pointer items-center justify-between space-x-2 border-b border-[#3C3C3C] px-4 py-3 transition-colors duration-200 last:border-b-0',
                  //   isSelected ? 'bg-[#BAFF38]/[10%]' : 'hover:bg-white/5',
                )}
                onClick={() => handleOptionToggle(option.value)}
              >
                <label
                  htmlFor={`${name}-${option.value}`}
                  className={cn(
                    'w-full cursor-pointer text-sm text-white transition-colors duration-200',
                    isSelected && 'font-semibold',
                  )}
                >
                  {option.label}
                </label>
                <input
                  type="checkbox"
                  id={`${name}-${option.value}`}
                  checked={isSelected}
                  readOnly
                  className="size-4 rounded-sm border border-[#AAACA6] bg-transparent text-[#BAFF38] accent-[#BAFF38]"
                />
              </div>
            );
          })}
        </PopoverContent>
      </Popover>

      {errors[name]?.message && (
        <Text variant="xs" className="text-rose-500">
          {errors[name]?.message?.toString()}
        </Text>
      )}
    </Col>
  );
}
