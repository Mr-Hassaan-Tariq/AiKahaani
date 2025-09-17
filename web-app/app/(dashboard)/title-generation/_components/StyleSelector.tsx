'use client';

import { useState } from 'react';

const styleOptions = [
  'Controversial',
  'Shocking',
  'Persuasive',
  'Sarcastic',
  'Witty',
  'Neutral',
  'Mysterious',
  'Dramatic',
  'Question-based',
];

export default function StyleSelector() {
  const [selected, setSelected] = useState<string[]>([]);

  const handleSelect = (option: string) => {
    if (selected.includes(option)) {
      // unselect
      setSelected(selected.filter((item) => item !== option));
    } else {
      // select only if less than 3
      if (selected.length < 3) {
        setSelected([...selected, option]);
      }
    }
  };

  return (
    <div className="flex flex-wrap gap-2">
      {styleOptions.map((option) => {
        const isSelected = selected.includes(option);
        return (
          <button
            type="button"
            key={option}
            onClick={() => handleSelect(option)}
            className={`rounded-full px-[12px] py-[8px] text-sm font-medium transition ${
              isSelected
                ? 'border border-[#BAFF381F] bg-[#FFFFFF1A] text-white'
                : 'border border-transparent bg-[#FFFFFF1A] text-[#AAACA6]'
            }`}
          >
            {option}
          </button>
        );
      })}
    </div>
  );
}
