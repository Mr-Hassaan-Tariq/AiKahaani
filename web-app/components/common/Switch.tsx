import { useState } from 'react';

interface SwitchProps {
  label: string;
  description?: string;
  defaultChecked?: boolean;
  disabled?: boolean;
  onToggle?: (checked: boolean) => void;
}

export default function Switch({
  label,
  description,
  defaultChecked = false,
  disabled = false,
  onToggle,
}: SwitchProps) {
  const [checked, setChecked] = useState(defaultChecked);

  const handleToggle = () => {
    if (disabled) return;
    setChecked(!checked);
    onToggle?.(!checked);
  };

  return (
    <div className="flex items-start gap-2 py-1 lg:items-center">
      <button
        onClick={handleToggle}
        className={`flex h-6 w-12 items-center rounded-full p-1 transition ${
          checked ? 'bg-white' : 'bg-[#2d2d2d]'
        } ${disabled ? 'cursor-not-allowed opacity-50' : ''}`}
      >
        <div
          className={`h-4 w-4 transform rounded-full shadow-md transition ${
            checked ? 'translate-x-6 bg-[#0E0F0C]' : 'translate-x-0 bg-white'
          }`}
        />
      </button>
      <div className="w-[240px] md:w-full lg:w-full">
        <p className="font-medium text-white">{label}</p>
        {description && <p className="text-sm text-gray-400">{description}</p>}
      </div>
    </div>
  );
}
