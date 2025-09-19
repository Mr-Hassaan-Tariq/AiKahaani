import { useMemo, useState } from 'react';
import { ChevronDown, X } from 'lucide-react';
import { useFormContext } from 'react-hook-form';

import { ToneType } from '../types';
import InfoModal from './InfoModal';
import { cn } from 'lib/utils';
import Col from 'components/ui/Col';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';
import { Popover, PopoverContent, PopoverTrigger } from 'components/shadcn_ui/popover';

export default function VibeToneWidget({ tones, name }: { tones: ToneType[]; name: string }) {
  const [open, setOpen] = useState(false);

  const {
    register,
    watch,
    formState: { errors },
  } = useFormContext();

  const { onChange } = register(name, {
    required: 'Tones are required',
    validate: (value: number[]) => {
      if (!Array.isArray(value)) return 'Tones must be an array';
      if (value.length < 1) return 'You must select at least 1 tone';
      if (value.length > 3) return 'You can only select up to 3 tones';
      return true;
    },
  });

  const handleTopicToggle = (toneId: number) => {
    const prev: number[] = watch(name);
    onChange({
      target: {
        name,
        value: prev.includes(toneId) ? prev.filter((id) => id !== toneId) : [...prev, toneId],
      },
    });
  };

  const selectedTopics = useMemo(() => {
    return tones.filter((tone) => watch(name).includes(tone.id));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [name, tones, watch(name)]);

  return (
    <Col className="gap-2">
      <Text variant="base" className="font-medium text-white">
        <Row className="justify-normal gap-2">
          <span>What&apos;s your video about?</span>
          <InfoModal description="Choose up to 3 tones to match your brand or content goal" />
        </Row>
      </Text>

      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger
          asChild
          className="data-[state=open]:border data-[state=open]:border-[#BAFF38]/[12%]"
        >
          <div className="flex h-14 w-full items-center justify-between rounded-2xl bg-white/10 px-4 text-brand-secondary">
            <span className="text-left text-base font-medium">
              Choose up to 3 tones (e.g. Informative, Motivational...)
            </span>
            <ChevronDown size={20} />
          </div>
        </PopoverTrigger>
        <Row className="mt-1 flex-wrap justify-normal gap-6">
          {selectedTopics?.map((tone) => (
            <Row key={tone.id.toString()} className="text-white hover:text-brand-secondary">
              <Text variant="sm" className="font-medium">
                {tone.name}
              </Text>
              <X size={16} className="cursor-pointer" onClick={() => handleTopicToggle(tone.id)} />
            </Row>
          ))}
        </Row>
        <PopoverContent
          className="w-[var(--radix-popover-trigger-width)] border-[#BAFF38]/[12%] bg-[#2D2D2D] p-0"
          align="start"
        >
          {tones.map((tone) => (
            <div
              key={tone.id.toString()}
              className="flex w-full items-center justify-between space-x-2 border-b border-[#BAFF38]/[12%] px-4 py-3 hover:bg-white/5"
            >
              <label
                htmlFor={tone.id.toString()}
                className={cn(
                  'w-full cursor-pointer text-base text-brand-secondary',
                  selectedTopics.some((topic) => topic.id === tone.id) && 'font-bold text-white',
                )}
              >
                {tone.name}
              </label>
              <input
                type="checkbox"
                id={tone.id.toString()}
                checked={selectedTopics.some((topic) => topic.id === tone.id)}
                onChange={() => handleTopicToggle(tone.id)}
                className="size-6 rounded-md accent-white"
              />
            </div>
          ))}
        </PopoverContent>
      </Popover>
      {errors[name]?.message && (
        <Text variant="xs" className="text-rose-500">
          {errors[name]?.message?.toString()}
        </Text>
      )}
    </Col>
  );
}
