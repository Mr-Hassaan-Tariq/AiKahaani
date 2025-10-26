'use client';

import { useState } from 'react';

import { Fire, SmileTone, VedioIconWhite } from './components';
import Button from 'components/ui/Button';
import Dialog from 'components/ui/Dialog';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';
import { Checkbox } from 'components/shadcn_ui/checkbox';

interface FilterModalProps {
  trigger: React.ReactNode;
  onApply: (filters: Record<string, string[]>) => void;
}

export default function FilterNicheModal({ trigger, onApply }: FilterModalProps) {
  const [open, setOpen] = useState(false);
  const [filters, setFilters] = useState<Record<string, string[]>>({
    Tone: [],
    Format: [],
    Popularity: [],
  });

  const handleToggle = (category: string, value: string) => {
    setFilters((prev) => {
      const values = prev[category] || [];
      return {
        ...prev,
        [category]: values.includes(value) ? values.filter((v) => v !== value) : [...values, value],
      };
    });
  };

  const sections: Record<string, { icon: any; options: string[] }> = {
    Tone: {
      icon: SmileTone,
      options: ['Emotional', 'Satirical', 'Bold', 'Informative'],
    },
    Format: {
      icon: VedioIconWhite,
      options: ['Storytelling', 'Review', '40 min', '60 min'],
    },
    Popularity: {
      icon: Fire,
      options: ['Hype', 'Classic', 'Trending', 'New'],
    },
  };

  return (
    <Dialog
      open={open}
      setOpen={(value) => setOpen(value)}
      trigger={trigger}
      title="Filter my niches"
      description=""
      footer={
        <Row className="w-full gap-6">
          <Button variant="gray">
            <Text
              variant="base"
              className="font-extrabold [font-feature-settings:'liga'_off,'clig'_off]"
            >
              Cancel
            </Text>
          </Button>
          <Button type="submit" variant="green" onClick={() => onApply(filters)}>
            Apply filters
          </Button>
        </Row>
      }
    >
      <div className="my-4 space-y-6">
        {Object.entries(sections).map(([category, { icon, options }]) => (
          <div key={category}>
            <h4 className="mb-2 flex gap-2 text-lg text-white">
              <span>{icon}</span> {category}:
            </h4>
            <div className="grid grid-cols-2 gap-2">
              {options.map((option) => (
                <label
                  key={option}
                  className="flex cursor-pointer items-center gap-2 text-sm text-[#AAACA6] hover:text-white"
                >
                  <Checkbox
                    checked={filters[category]?.includes(option)}
                    onCheckedChange={() => handleToggle(category, option)}
                    className="border-[#AAACA6]"
                  />
                  {option}
                </label>
              ))}
            </div>
          </div>
        ))}
      </div>
    </Dialog>
  );
}
