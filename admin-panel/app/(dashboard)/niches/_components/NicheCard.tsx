import { FC } from 'react';
import Image from 'next/image';
import { ExternalLink } from 'lucide-react';

import NicheStyleModal from './NicheStyleModal';
import VedioModal from './VedioModal';
import Button from 'components/ui/Button';
import Card from 'components/ui/Card';
import Text from 'components/ui/Text';

interface NicheCardProps {
  id: number;
  title: string;
  description: string;
  tone: string[];
  pacing: string[];
  topChannels: { name: string; link: string }[];
  thumbnailUrl?: string | null;
}

const NicheCard: FC<NicheCardProps> = ({
  id,
  title,
  description,
  tone,
  pacing,
  topChannels,
  thumbnailUrl,
}) => {
  const tags = [...(tone || []), ...(pacing || [])];
  const examples = topChannels?.map((c) => c.name) || [];

  const videoUrl = topChannels[0]?.link || '';

  const truncated = examples.join(', ');
  const maxLength = 35;
  const displayText =
    truncated.length > maxLength ? truncated.substring(0, maxLength) + '...' : truncated;

  return (
    <Card className="rounded-xl bg-[#161616] text-white lg:px-5 lg:py-5">
      <div className="relative h-40">
        {thumbnailUrl ? (
          <VedioModal
            trigger={
              <Image src={thumbnailUrl} alt={title} fill className="rounded-xl object-cover" />
            }
            title={title}
            videoId={'videoId'}
            subtitle={description}
            youtubeUrl={videoUrl}
            thumbnailUrl={thumbnailUrl}
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center rounded-xl bg-[#2a2a2a] text-center text-lg font-semibold text-white">
            Thumbnail
          </div>
        )}
      </div>

      <div className="mt-4 space-y-3">
        <div className="flex flex-wrap items-center justify-between text-xs text-gray-300">
          <div className="rounded-md border border-[#BAFF381F] bg-[#2a2a2a] p-2">
            {tags.length > 0 ? (
              tags.map((tag, i) => (
                <span key={i} className="text-white">
                  {tag}
                  {i < tags.length - 1 && ', '}
                </span>
              ))
            ) : (
              <span className="text-gray-400">No tags</span>
            )}
          </div>
          <ExternalLink className="h-5 w-5 cursor-pointer text-white" />
        </div>

        <Text className="text-xl font-semibold">{title}</Text>
        <Text variant="base" className="text-[#AAACA6]">
          {description}
        </Text>

        <Text variant="base" className="text-[#AAACA6]">
          Examples:{' '}
          <span className="text-white">{examples.length > 0 ? displayText : 'No examples'}</span>
        </Text>

        <NicheStyleModal trigger={<Button variant="green">View Details</Button>} nicheId={id} />
      </div>
    </Card>
  );
};

export default NicheCard;
