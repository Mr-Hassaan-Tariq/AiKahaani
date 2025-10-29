'use client';

import { useEffect, useMemo, useState } from 'react';

import { Fire, SmileTone, VedioIconWhite } from './components';
import Button from 'components/ui/Button';
import Dialog from 'components/ui/Dialog';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';
import { Checkbox } from 'components/shadcn_ui/checkbox';

interface FilterModalProps {
  trigger: React.ReactNode;
  availableFilters?: Record<string, string[]>;
  onApply: (filters: Record<string, string[]>) => void;
}

export default function FilterNicheModal({ trigger, availableFilters, onApply }: FilterModalProps) {
  const defaultSections: Record<string, string[]> = {
    Tone: ['Educational', 'Casual', 'Emotional', 'Satirical', 'Bold', 'Informative'],
    Format: ['Storytelling', 'Review', 'Explainer', 'Interview'],
    Popularity: ['Hype', 'Classic', 'Trending', 'New'],
  };

  const sections = availableFilters || defaultSections;

  const initialFilters = useMemo(
    () => Object.keys(sections).reduce((acc, k) => ({ ...acc, [k]: [] as string[] }), {}),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [JSON.stringify(sections)],
  );

  const [open, setOpen] = useState(false);
  const [filters, setFilters] = useState<Record<string, string[]>>(initialFilters);

  useEffect(() => {
    setFilters((prev) =>
      Object.keys(sections).reduce((acc, k) => ({ ...acc, [k]: prev[k] || [] }), {}),
    );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(sections)]);

  const handleToggle = (category: string, value: string) => {
    setFilters((prev) => {
      const values = prev[category] || [];
      return {
        ...prev,
        [category]: values.includes(value) ? values.filter((v) => v !== value) : [...values, value],
      };
    });
  };

  const handleApply = () => {
    onApply(filters);
    setOpen(false);
  };

  const handleReset = () => {
    setFilters(initialFilters);
    onApply(initialFilters);
    setOpen(false);
  };

  const isAnyFilterSelected = Object.values(filters).some((arr) => arr.length > 0);

  return (
    <Dialog
      open={open}
      setOpen={(value) => setOpen(value)}
      trigger={trigger}
      title="Filter niches"
      description=""
      footer={
        <Row className="w-full gap-3">
          <Button variant="gray" onClick={() => setOpen(false)}>
            <Text variant="base" className="font-extrabold">
              Cancel
            </Text>
          </Button>

          {isAnyFilterSelected && (
            <Button
              type="button"
              variant="gray"
              onClick={handleReset}
              className="border border-white/10 bg-transparent text-white/80 hover:bg-white/5"
            >
              Reset
            </Button>
          )}

          <Button
            type="button"
            variant="green"
            onClick={handleApply}
            disabled={!isAnyFilterSelected}
            className={`transition-all duration-200 ${
              !isAnyFilterSelected
                ? 'cursor-not-allowed opacity-50'
                : 'hover:bg-white/90 hover:text-black'
            }`}
          >
            Apply filters
          </Button>
        </Row>
      }
    >
      <div className="my-4 space-y-6">
        {Object.entries(sections).map(([category, options]) => (
          <div key={category}>
            <h4 className="mb-2 flex gap-2 text-lg text-white">
              <span>
                {category === 'Tone' ? (
                  <SmileTone />
                ) : category === 'Popularity' ? (
                  <Fire />
                ) : (
                  <VedioIconWhite />
                )}
              </span>
              {category}
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
