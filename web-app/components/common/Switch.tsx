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
    <div className="flex items-start gap-3 py-1 lg:items-center">
      <button
        type="button"
        onClick={handleToggle}
        aria-checked={checked}
        role="switch"
        className={`relative flex h-6 w-11 shrink-0 items-center rounded-full p-0.5 transition-colors ${
          checked ? 'bg-primary' : 'bg-border'
        } ${disabled ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'}`}
      >
        <div
          className={`h-5 w-5 transform rounded-full bg-white shadow-sm transition-transform ${
            checked ? 'translate-x-5' : 'translate-x-0'
          }`}
        />
      </button>
      <div className="min-w-0">
        <p className="text-sm font-medium text-foreground">{label}</p>
        {description && <p className="mt-0.5 text-xs text-muted-foreground">{description}</p>}
      </div>
    </div>
  );
}
