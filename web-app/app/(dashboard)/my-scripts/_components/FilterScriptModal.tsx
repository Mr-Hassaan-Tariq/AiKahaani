'use client';

import { useEffect, useState } from 'react';
import { Clock, FileText, Video } from 'lucide-react';
import deepEqual from 'fast-deep-equal';

import { FiltersState } from '../_utils/filterUtils';
import { Button } from 'components/ui/Button';
import Dialog from 'components/ui/Dialog';
import { Checkbox } from 'components/shadcn_ui/checkbox';
import { RadioGroup, RadioGroupItem } from 'components/shadcn_ui/radio-group';
import { Slider } from 'components/shadcn_ui/slider';

interface FilterScriptModalProps {
  trigger: React.ReactNode;
  onApplyFilters?: (filters: FiltersState) => void;
  onClearFilters?: () => void;
  initialFilters?: Partial<FiltersState>;
}

export const defaultFilters: FiltersState = {
  lastEdited: 'most_recent',
  wordCount: [1000, 2000],
  videoDuration: null,
};

const durations = [
  { id: '<20', label: '< 20 min' },
  { id: '20', label: '20 min' },
  { id: '40', label: '40 min' },
  { id: '60', label: '60 min' },
  { id: '>60', label: '> 60 min' },
];

export default function FilterScriptModal({
  trigger,
  onApplyFilters,
  onClearFilters,
  initialFilters = {},
}: FilterScriptModalProps) {
  const [open, setOpen] = useState(false);
  const [filters, setFilters] = useState<FiltersState>({ ...defaultFilters, ...initialFilters });

  useEffect(() => {
    setFilters({ ...defaultFilters, ...initialFilters });
  }, [initialFilters]);

  const updateFilter = <K extends keyof FiltersState>(key: K, value: FiltersState[K]) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const hasActiveFilters = !deepEqual(defaultFilters, { ...defaultFilters, ...filters });

  return (
    <Dialog
      open={open}
      setOpen={setOpen}
      trigger={trigger}
      title="Filter scripts"
      description=""
      footer={
        <div className="flex w-full gap-2">
          <Button variant="outline" className="flex-1" onClick={() => { setFilters({ ...defaultFilters, ...initialFilters }); setOpen(false); }}>
            Cancel
          </Button>
          {onClearFilters && (
            <Button variant="outline" onClick={() => { setFilters({ ...defaultFilters }); onClearFilters?.(); setOpen(false); }} disabled={!hasActiveFilters}>
              Clear
            </Button>
          )}
          <Button className="flex-1" onClick={() => { onApplyFilters?.(filters); setOpen(false); }}>
            Apply
          </Button>
        </div>
      }
    >
      <div className="flex flex-col gap-5 my-2">
        {/* Last Edited */}
        <div>
          <p className="mb-3 flex items-center gap-2 text-sm font-medium text-foreground">
            <Clock className="h-4 w-4" /> Last edited
          </p>
          <RadioGroup
            value={filters.lastEdited}
            onValueChange={(val) => updateFilter('lastEdited', val)}
            className="flex gap-6"
          >
            {[{ value: 'most_recent', label: 'Most recent' }, { value: 'oldest', label: 'Oldest' }].map((opt) => (
              <div key={opt.value} className="flex items-center gap-2">
                <RadioGroupItem value={opt.value} id={opt.value} />
                <label htmlFor={opt.value} className="cursor-pointer text-sm text-foreground">{opt.label}</label>
              </div>
            ))}
          </RadioGroup>
        </div>

        {/* Word Count */}
        <div>
          <p className="mb-3 flex items-center gap-2 text-sm font-medium text-foreground">
            <FileText className="h-4 w-4" /> Word count
          </p>
          <Slider
            value={filters.wordCount}
            onValueChange={(val) => updateFilter('wordCount', val as [number, number])}
            max={10000}
            step={10}
          />
          <div className="mt-2 flex justify-between text-xs text-muted-foreground">
            <span>{filters.wordCount[0].toLocaleString()} words</span>
            <span>{filters.wordCount[1].toLocaleString()} words</span>
          </div>
        </div>

        {/* Video Duration */}
        <div>
          <p className="mb-3 flex items-center gap-2 text-sm font-medium text-foreground">
            <Video className="h-4 w-4" /> Estimated duration
          </p>
          <div className="grid grid-cols-2 gap-2">
            {durations.map((d) => (
              <label key={d.id} className="flex cursor-pointer items-center gap-2 rounded-lg border border-border p-2 transition-colors hover:bg-accent has-[:checked]:border-primary">
                <Checkbox
                  checked={filters.videoDuration === d.id}
                  onCheckedChange={() => updateFilter('videoDuration', filters.videoDuration === d.id ? null : d.id)}
                />
                <span className="text-sm text-foreground">{d.label}</span>
              </label>
            ))}
          </div>
        </div>
      </div>
    </Dialog>
  );
}
