import { cn } from 'lib/utils';
import useGetTitleStyles from 'lib/hooks/useGetTitleStyles';

export default function StyleSelector({
  value,
  onChange,
  error,
}: {
  value: string[];
  onChange: (tones: string[]) => void;
  error?: string;
}) {
  const { data } = useGetTitleStyles();
  if (!data) return null;

  const handleSelect = (option: string) => {
    if (value.includes(option)) {
      onChange(value.filter((item) => item !== option));
    } else if (value.length < 3) {
      onChange([...value, option]);
    }
  };

  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-wrap gap-2">
        {data?.results?.map((tone: { id: number; name: string }) => {
          const isSelected = value.includes(tone.name);
          return (
            <button
              type="button"
              key={tone.id}
              onClick={() => handleSelect(tone.name)}
              className={cn(
                'rounded-md border px-3 py-1.5 text-sm font-medium transition-colors',
                isSelected
                  ? 'border-primary bg-accent text-accent-foreground'
                  : 'border-border bg-transparent text-muted-foreground hover:border-primary/40 hover:bg-muted hover:text-foreground',
              )}
            >
              {tone.name}
            </button>
          );
        })}
      </div>
      {error && <p className="text-xs text-destructive">{error}</p>}
    </div>
  );
}
