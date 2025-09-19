import { Controller } from 'react-hook-form';

import StyleSelector from './StyleSelector';

export default function ToneSelector({ control }: any) {
  return (
    <Controller
      name="tones"
      control={control}
      rules={{
        required: 'Please select at least one tone',
        validate: (val) => (val.length > 0 && val.length <= 3) || 'Select between 1 and 3 tones',
      }}
      render={({ field, fieldState }) => (
        <StyleSelector
          value={field.value}
          onChange={field.onChange}
          error={fieldState.error?.message}
        />
      )}
    />
  );
}
