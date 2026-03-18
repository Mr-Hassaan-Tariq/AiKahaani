'use client';

import { useEffect, useMemo, useState } from 'react';
import { Flame, Smile, Video } from 'lucide-react';

import { cn } from 'lib/utils';
import Button from 'components/ui/Button';
import Dialog from 'components/ui/Dialog';
import { Checkbox } from 'components/shadcn_ui/checkbox';

interface FilterModalProps {
  trigger: React.ReactNode;
  availableFilters?: Record<string, string[]>;
  onApply: (filters: Record<string, string[]>) => void;
  initialFilters?: Record<string, string[]>;
}

const categoryIcon: Record<string, React.ReactNode> = {
  Tone: <Smile className="h-5 w-5" />,
  Popularity: <Flame className="h-5 w-5" />,
};

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
  const [filters, setFilters] = useState<Record<string, string[]>>(initialFiltersFromSections);

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

  const isAnyFilterSelected = Object.values(filters).some((arr) => arr.length > 0);

  return (
    <Dialog
      open={open}
      setOpen={(value) => setOpen(value)}
      trigger={trigger}
      title="Filter niches"
      description=""
      footer={
        <div className="flex w-full gap-3">
          <Button variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>

          {isAnyFilterSelected && (
            <Button variant="outline" type="button" onClick={handleReset}>
              Reset
            </Button>
          )}

          <Button type="button" onClick={handleApply} disabled={!isAnyFilterSelected}>
            Apply filters
          </Button>
        </div>
      }
    >
      <div className="my-4 space-y-6">
        {Object.entries(sections).map(([category, options]) => (
          <div key={category}>
            <h4 className="mb-3 flex items-center gap-2 text-sm font-semibold text-foreground">
              <span className="text-muted-foreground">
                {categoryIcon[category] ?? <Video className="h-5 w-5" />}
              </span>
              {category}
            </h4>

            <div className="grid grid-cols-2 gap-2">
              {options.map((option) => (
                <label
                  key={option}
                  className={cn(
                    'flex cursor-pointer items-center gap-2 rounded-lg border border-border px-3 py-2 text-sm transition-colors',
                    filters[category]?.includes(option)
                      ? 'border-primary bg-accent text-foreground'
                      : 'text-muted-foreground hover:border-primary/40 hover:bg-muted hover:text-foreground',
                  )}
                >
                  <Checkbox
                    checked={filters[category]?.includes(option)}
                    onCheckedChange={() => handleToggle(category, option)}
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
