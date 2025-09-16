import { useState } from 'react';
import { ChevronDown, X } from 'lucide-react';

import InfoModal from './InfoModal';
import { cn } from 'lib/utils';
import Col from 'components/ui/Col';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';
import { Popover, PopoverContent, PopoverTrigger } from 'components/shadcn_ui/popover';

export default function VibeToneWidget() {
  const [selectedTopics, setSelectedTopics] = useState<string[]>([]);
  const [open, setOpen] = useState(false);

  const handleTopicToggle = (topicId: string) => {
    setSelectedTopics((prev) =>
      prev.includes(topicId) ? prev.filter((id) => id !== topicId) : [...prev, topicId],
    );
  };

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
          {selectedTopics?.map((topic) => (
            <Row key={topic} className="text-white hover:text-brand-secondary">
              <Text variant="sm" className="font-medium">
                {topic}
              </Text>
              <X size={16} className="cursor-pointer" onClick={() => handleTopicToggle(topic)} />
            </Row>
          ))}
        </Row>
        <PopoverContent
          className="w-[var(--radix-popover-trigger-width)] border-[#BAFF38]/[12%] bg-[#2D2D2D] p-0"
          align="start"
        >
          {videoTopics.map((topic) => (
            <div
              key={topic}
              className="flex w-full items-center justify-between space-x-2 border-b border-[#BAFF38]/[12%] px-4 py-3 hover:bg-white/5"
            >
              <label
                htmlFor={topic}
                className={cn(
                  'w-full cursor-pointer text-base text-brand-secondary',
                  selectedTopics.includes(topic) && 'font-bold text-white',
                )}
              >
                {topic}
              </label>
              <input
                type="checkbox"
                id={topic}
                checked={selectedTopics.includes(topic)}
                onChange={() => handleTopicToggle(topic)}
                className="size-6 rounded-md accent-white"
              />
            </div>
          ))}
        </PopoverContent>
      </Popover>
    </Col>
  );
}

// Video topic options
const videoTopics = ['Informative', 'Professional', 'Entertaining', 'Motivational', 'Funny'];
