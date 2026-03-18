import { useEffect } from 'react';
import { FileText, PencilLine } from 'lucide-react';

import ScriptSelector from './ScriptSelector';
import FormInput from 'components/ui/FormInput';
import { cn } from 'lib/utils';

const SOURCE_OPTIONS = [
  {
    value: 'saved',
    icon: FileText,
    label: 'Use a saved script',
    description: 'Pick from your drafts and let the AI refine its title.',
  },
  {
    value: 'manual',
    icon: PencilLine,
    label: 'Enter a title manually',
    description: 'Paste any existing title and get optimized alternatives.',
  },
];

export default function OptimizeFormFields({ watch, scripts, register, resetField, setValue }: any) {
  const duration = watch('duration');

  useEffect(() => {
    if (duration === 'saved') { resetField('manualTitle'); setValue('scriptOption', ''); }
    else if (duration === 'manual') { resetField('scriptOption'); setValue('manualTitle', ''); }
  }, [duration]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="flex flex-col gap-5">
      {/* Source selection cards */}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {SOURCE_OPTIONS.map((opt) => {
          const isSelected = duration === opt.value;
          const Icon = opt.icon;
          return (
            <label
              key={opt.value}
              className={cn(
                'flex items-start gap-4 rounded-xl border p-5 cursor-pointer transition-colors',
                isSelected
                  ? 'border-primary/30 bg-gradient-to-b from-primary/[0.04] to-card'
                  : 'border-border bg-card hover:bg-muted/50',
              )}
            >
              <input
                type="radio"
                value={opt.value}
                {...register('duration')}
                className="sr-only"
              />
              <div className={cn(
                'mt-0.5 w-9 h-9 shrink-0 rounded-lg flex items-center justify-center',
                isSelected ? 'bg-primary/10 text-primary' : 'bg-secondary text-muted-foreground',
              )}>
                <Icon className="h-[18px] w-[18px]" />
              </div>
              <div className="min-w-0">
                <p className={cn(
                  'text-sm font-semibold leading-snug',
                  isSelected ? 'text-foreground' : 'text-muted-foreground',
                )}>
                  {opt.label}
                </p>
                <p className="mt-1 text-xs text-muted-foreground leading-relaxed">
                  {opt.description}
                </p>
              </div>
            </label>
          );
        })}
      </div>

      {/* Conditional input */}
      {duration === 'saved' && (
        <ScriptSelector
          name="scriptOption"
          scripts={(scripts ?? []).map((s: any) => ({
            uuid: String(s.uuid),
            title: s.title,
            outline_title: s.outline_title,
          }))}
        />
      )}

      {duration === 'manual' && (
        <FormInput
          name="manualTitle"
          label="Your existing title"
          placeholder="Paste or type your current title here…"
          validationSchema={{
            required: 'Title is required',
            minLength: { value: 10, message: 'Title must be at least 10 characters' },
          }}
        />
      )}
    </div>
  );
}
