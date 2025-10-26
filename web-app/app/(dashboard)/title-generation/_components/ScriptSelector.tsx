'use client';

import { useMemo, useState } from 'react';
import Image from 'next/image';
import { ChevronDown } from 'lucide-react';
import { useFormContext } from 'react-hook-form';

import InfoIcon from '/public/images/info.svg';
import { cn } from 'lib/utils';
import Col from 'components/ui/Col';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';
import { Popover, PopoverContent, PopoverTrigger } from 'components/shadcn_ui/popover';

export default function ScriptSelector({
  scripts = [],
  name,
}: {
  scripts: { uuid: string; title: string; outline_title?: string }[];
  name: string;
}) {
  const [open, setOpen] = useState(false);

  const {
    register,
    watch,
    formState: { errors },
  } = useFormContext();

  const { onChange } = register(name, {
    required: 'Please select a script option',
  });

  const selectedValue = watch(name);
  const selectedScript = useMemo(
    () => scripts.find((s) => s.uuid === selectedValue),
    [selectedValue, scripts],
  );

  const handleSelect = (uuid: string) => {
    onChange({ target: { name, value: uuid } });
    setOpen(false);
  };

  return (
    <Col className="gap-2">
      <Row className="mt-6 flex items-center justify-start gap-2">
        <Text className="text-md mb-2 text-left text-white">
          Select from a saved or draft script
        </Text>
        <Image className="mt-[-8px]" src={InfoIcon} alt="info-icon" width={16} height={16} />
      </Row>

      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger
          asChild
          className="data-[state=open]:border data-[state=open]:border-[#BAFF38]/[12%]"
        >
          <div className="flex h-14 w-full cursor-pointer items-center justify-between rounded-2xl bg-white/10 px-4 text-brand-secondary">
            <span className="truncate text-left text-base font-medium">
              {selectedScript ? selectedScript.title : 'Select a script'}
            </span>
            <ChevronDown size={20} />
          </div>
        </PopoverTrigger>

        <PopoverContent
          className="w-[var(--radix-popover-trigger-width)] border-[#BAFF38]/[12%] bg-[#2D2D2D] p-0"
          align="start"
        >
          {scripts?.map((script) => {
            const isSelected = selectedValue === script.uuid;
            return (
              <div
                key={script.uuid}
                className="flex w-full cursor-pointer items-center justify-between border-b border-[#BAFF38]/[12%] px-4 py-3 hover:bg-white/5"
                onClick={() => handleSelect(script.uuid)}
              >
                <label
                  className={cn(
                    'w-full cursor-pointer text-base text-brand-secondary',
                    isSelected && 'font-bold text-white',
                  )}
                >
                  {script.title.length > 50 ? `${script.title.substring(0, 50)}...` : script.title}
                </label>
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
