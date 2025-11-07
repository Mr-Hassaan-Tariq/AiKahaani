'use client';

import { useEffect, useState } from 'react';
import deepEqual from 'fast-deep-equal';

import { FiltersState } from '../_utils/filterUtils';
import { NoteIcon, TimeIcon, VideoIcon } from './components';
import Button from 'components/ui/Button';
import Dialog from 'components/ui/Dialog';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';
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

export default function FilterScriptModal({
  trigger,
  onApplyFilters,
  onClearFilters,
  initialFilters = {},
}: FilterScriptModalProps) {
  const [open, setOpen] = useState(false);

  // internal filters (syncs with initialFilters)
  const [filters, setFilters] = useState<FiltersState>({
    ...defaultFilters,
    ...initialFilters,
  });

  // sync whenever parent updates initialFilters
  useEffect(() => {
    setFilters({
      ...defaultFilters,
      ...initialFilters,
    });
  }, [initialFilters]);

  const updateFilter = <K extends keyof FiltersState>(key: K, value: FiltersState[K]) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleApplyFilters = () => {
    onApplyFilters?.(filters);
    setOpen(false);
  };

  const handleCancel = () => {
    // revert to whatever parent currently says
    setFilters({ ...defaultFilters, ...initialFilters });
    setOpen(false);
  };

  const handleClear = () => {
    const cleared = { ...defaultFilters };
    setFilters(cleared);
    onClearFilters?.();
    setOpen(false);
  };

  // whether modal currently has any non-default filters
  const hasActiveFilters = !deepEqual(
    { ...defaultFilters },
    {
      ...defaultFilters,
      ...filters,
    },
  );

  const durations = [
    { id: '<20', label: '< 20 min' },
    { id: '20', label: '20 min' },
    { id: '40', label: '40 min' },
    { id: '60', label: '60 min' },
    { id: '>60', label: '> 60 min' },
  ];

  return (
    <Dialog
      open={open}
      setOpen={setOpen}
      trigger={trigger}
      title="Filter my scripts"
      description=""
      footer={
        <Row className="w-full gap-6">
          <Button variant="gray" onClick={handleCancel}>
            <Text variant="base" className="font-extrabold">
              Cancel
            </Text>
          </Button>

          {/* Disable/hide Clear when no active filters */}
          {onClearFilters && (
            <Button variant="gray" onClick={handleClear} disabled={!hasActiveFilters}>
              <Text variant="base" className="font-extrabold">
                Clear filters
              </Text>
            </Button>
          )}

          <Button variant="green" onClick={handleApplyFilters}>
            Apply filters
          </Button>
        </Row>
      }
    >
      <>
        {/* Last Edited */}
        <div className="my-4">
          <p className="mb-2 flex items-center gap-2 font-medium">
            <span>{TimeIcon}</span> Last edited:
          </p>
          <RadioGroup
            value={filters.lastEdited}
            onValueChange={(val) => updateFilter('lastEdited', val)}
            className="flex gap-6"
          >
            <div className="flex items-center space-x-2">
              <RadioGroupItem
                value="most_recent"
                id="most_recent"
                className="border-[#3b3b3b] text-white data-[state=checked]:border-white"
              />
              <Text>Most recent</Text>
            </div>
            <div className="flex items-center space-x-2">
              <RadioGroupItem
                value="oldest"
                id="oldest"
                className="border-[#3b3b3b] text-white data-[state=checked]:border-white"
              />
              <Text>Oldest</Text>
            </div>
          </RadioGroup>
        </div>

        {/* Word Count */}
        <div className="my-4">
          <p className="mb-3 flex items-center gap-2 font-medium">
            <span>{NoteIcon}</span> Word count:
          </p>

          {/* Controlled slider so it always reflects `filters.wordCount` */}
          <Slider
            value={filters.wordCount}
            onValueChange={(val) => updateFilter('wordCount', val as [number, number])}
            max={10000}
            step={10}
            className="h-2"
          />

          <Row className="mt-3">
            <Text variant="xs" className="text-[#AAACA6]">
              {filters.wordCount[1] - filters.wordCount[0]} words
            </Text>
            <Text variant="xs" className="text-[#AAACA6]">
              10,000 words
            </Text>
          </Row>
        </div>

        {/* Estimated video duration */}
        <div className="my-4">
          <p className="mb-2 flex items-center gap-2 font-medium">
            <span>{VideoIcon}</span> Estimated video duration
          </p>
          <div className="grid grid-cols-2 gap-3">
            {durations.map((d) => (
              <div key={d.id} className="flex items-center space-x-2">
                <Checkbox
                  checked={filters.videoDuration === d.id}
                  onCheckedChange={() =>
                    updateFilter('videoDuration', filters.videoDuration === d.id ? null : d.id)
                  }
                  className="border-[#3b3b3b] data-[state=checked]:border-white"
                />
                <Text>{d.label}</Text>
              </div>
            ))}
          </div>
        </div>
      </>
    </Dialog>
  );
}
