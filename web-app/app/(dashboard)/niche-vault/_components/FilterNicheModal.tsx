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
  initialFilters?: Record<string, string[]>; // new prop to receive parent state
}

export default function FilterNicheModal({
  trigger,
  availableFilters,
  onApply,
  initialFilters = {},
}: FilterModalProps) {
  const defaultSections: Record<string, string[]> = {
    Tone: ['Neutral', 'Professional', 'Educational', 'Engaging', 'Conversational', 'Storytelling'],
  };

  const sections = availableFilters || defaultSections;

  // create a normalized empty-map for categories
  const initialFiltersFromSections = useMemo(
    () =>
      Object.keys(sections).reduce(
        (acc, k) => {
          acc[k] = (
            initialFilters[k] && Array.isArray(initialFilters[k]) ? initialFilters[k] : []
          ) as string[];
          return acc;
        },
        {} as Record<string, string[]>,
      ),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [JSON.stringify(sections), JSON.stringify(initialFilters)],
  );

  const [open, setOpen] = useState(false);

  // internal modal state
  const [filters, setFilters] = useState<Record<string, string[]>>(initialFiltersFromSections);

  // Sync modal internal filters whenever parent initialFilters changes (so chip removals reflect inside modal)
  useEffect(() => {
    setFilters(initialFiltersFromSections);
  }, [initialFiltersFromSections]);

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
    const fresh: Record<string, string[]> = Object.keys(sections).reduce(
      (acc, k) => {
        acc[k] = [];
        return acc;
      },
      {} as Record<string, string[]>,
    );
    setFilters(fresh);
    onApply(fresh);
    setOpen(false);
  };

  // detect whether there are any active filters in modal
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
