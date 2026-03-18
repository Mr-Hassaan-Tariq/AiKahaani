import { useEffect } from 'react';

import ScriptSelector from './ScriptSelector';
import FormInput from 'components/ui/FormInput';
import { cn } from 'lib/utils';

export default function OptimizeFormFields({ watch, scripts, register, resetField, setValue }: any) {
  const duration = watch('duration');

  useEffect(() => {
    if (duration === 'saved') { resetField('manualTitle'); setValue('scriptOption', ''); }
    else if (duration === 'manual') { resetField('scriptOption'); setValue('manualTitle', ''); }
  }, [duration]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="flex flex-col gap-4">
      <div>
        <p className="mb-2 text-sm font-medium text-foreground">Script source</p>
        <div className="flex flex-col gap-2 sm:flex-row sm:gap-6">
          {[
            { value: 'saved', label: 'Use a saved draft or script' },
            { value: 'manual', label: 'Enter a title manually' },
          ].map((opt) => (
            <label key={opt.value} className="flex cursor-pointer items-center gap-2">
              <input
                type="radio"
                value={opt.value}
                {...register('duration')}
                className="peer h-4 w-4 cursor-pointer accent-primary"
              />
              <span className={cn(
                'text-sm text-muted-foreground transition-colors',
                'peer-checked:text-foreground peer-checked:font-medium',
              )}>
                {opt.label}
              </span>
            </label>
          ))}
        </div>
      </div>

      {watch('duration') === 'saved' && (
        <ScriptSelector
          name="scriptOption"
          scripts={(scripts ?? []).map((s: any) => ({
            uuid: String(s.uuid),
            title: s.title,
            outline_title: s.outline_title,
          }))}
        />
      )}

      {watch('duration') === 'manual' && (
        <FormInput
          name="manualTitle"
          label="Your title"
          placeholder="Enter your title manually…"
          validationSchema={{
            required: 'Title is required',
            minLength: { value: 10, message: 'Title must be at least 10 characters' },
          }}
        />
      )}
    </div>
  );
}
