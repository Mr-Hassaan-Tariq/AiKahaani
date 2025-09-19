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
    } else {
      if (value.length < 3) {
        onChange([...value, option]);
      }
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
              className={`rounded-full px-[12px] py-[8px] text-sm font-medium transition ${
                isSelected
                  ? 'border border-[#BAFF381F] bg-[#FFFFFF1A] text-white'
                  : 'border border-transparent bg-[#FFFFFF1A] text-[#AAACA6]'
              }`}
            >
              {tone.name}
            </button>
          );
        })}
      </div>
      {error && <p className="text-sm text-red-500">{error}</p>}
    </div>
  );
}
