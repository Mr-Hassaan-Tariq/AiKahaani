'use client';

import { useMemo, useState } from 'react';
import { ChevronDown } from 'lucide-react';
import { useFormContext } from 'react-hook-form';

import { cn } from 'lib/utils';
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
  const { onChange } = register(name, { required: 'Please select a script option' });
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
    <div className="flex flex-col gap-1.5">
      <label className="text-sm font-medium text-foreground">Select a saved or draft script</label>

      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <button
            type="button"
            className="flex h-11 w-full items-center justify-between rounded-xl border border-border bg-background px-4 text-sm text-foreground transition-colors hover:bg-muted/50 focus:outline-none focus:ring-2 focus:ring-ring"
          >
            <span className="truncate text-left">
              {selectedScript ? selectedScript.title : 'Select a script…'}
            </span>
            <ChevronDown className="ml-2 h-4 w-4 shrink-0 text-muted-foreground" />
          </button>
        </PopoverTrigger>

        <PopoverContent
          className="w-[var(--radix-popover-trigger-width)] border border-border bg-card p-0 shadow-md"
          align="start"
        >
          <div className="max-h-48 overflow-y-auto">
            {scripts.length === 0 ? (
              <p className="px-3 py-2 text-xs text-muted-foreground">No saved scripts found.</p>
            ) : (
              scripts.map((script) => {
                const isSelected = selectedValue === script.uuid;
                return (
                  <button
                    key={script.uuid}
                    type="button"
                    className={cn(
                      'flex w-full cursor-pointer items-center border-b border-border px-3 py-2.5 text-left text-sm transition-colors hover:bg-accent',
                      isSelected && 'bg-accent font-medium text-foreground',
                      !isSelected && 'text-muted-foreground',
                    )}
                    onClick={() => handleSelect(script.uuid)}
                  >
                    {script.title.length > 60 ? `${script.title.substring(0, 60)}…` : script.title}
                  </button>
                );
              })
            )}
          </div>
        </PopoverContent>
      </Popover>

      {errors[name]?.message && (
        <p className="text-xs text-destructive">{errors[name]?.message?.toString()}</p>
      )}
    </div>
  );
}
