'use client';

import { Clock } from 'lucide-react';
import { RegisterOptions, useFormContext } from 'react-hook-form';

import { TemplateStyleType } from '../types';
import { cn } from 'lib/utils';

export default function TemplatesWidget({
  templates,
  name,
  validationSchema,
}: {
  templates: TemplateStyleType[];
  name: string;
  validationSchema?: RegisterOptions;
}) {
  const {
    register,
    watch,
    formState: { errors },
  } = useFormContext();

  const { onChange } = register(name, validationSchema);
  const selected: number | undefined = watch(name);

  return (
    <div className="flex flex-col gap-3">
      {/* Label */}
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-foreground">Template style</span>
        <span className="text-xs text-muted-foreground">Optional</span>
      </div>

      {/* Card grid */}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {templates.map((template) => {
          const active = selected === template.id;
          return (
            <button
              key={template.id}
              type="button"
              onClick={() => {
                const newValue = active ? undefined : template.id;
                onChange({ target: { name, value: newValue } });
              }}
              className={cn(
                'flex flex-col gap-2 rounded-xl border p-4 text-left transition-colors',
                active
                  ? 'border-primary bg-accent'
                  : 'border-border bg-card hover:border-primary/30 hover:bg-muted/50',
              )}
            >
              <div className="flex items-center justify-between gap-2">
                <span
                  className={cn(
                    'text-sm font-semibold',
                    active ? 'text-accent-foreground' : 'text-foreground',
                  )}
                >
                  {template.name}
                </span>
                <span
                  className={cn(
                    'flex items-center gap-1 whitespace-nowrap text-xs',
                    active ? 'text-accent-foreground/70' : 'text-muted-foreground',
                  )}
                >
                  <Clock className="h-3 w-3" />~{template.duration}m · {template.word_range}
                </span>
              </div>
              <p
                className={cn(
                  'text-xs leading-relaxed',
                  active ? 'text-accent-foreground/80' : 'text-muted-foreground',
                )}
              >
                {template.description}
              </p>
            </button>
          );
        })}
      </div>

      {errors[name]?.message && (
        <p className="text-xs text-destructive">{errors[name]?.message?.toString()}</p>
      )}
    </div>
  );
}
