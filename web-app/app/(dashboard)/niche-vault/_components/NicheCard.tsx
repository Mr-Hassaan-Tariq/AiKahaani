import { FC } from 'react';
import Image from 'next/image';
import { ExternalLink } from 'lucide-react';

import NicheStyleModal from './NicheStyleModal';
import VedioModal from './VedioModal';
import Button from 'components/ui/Button';
import Card from 'components/ui/Card';
import Text from 'components/ui/Text';

interface NicheCardProps {
  image: any;
  title: string;
  description: string;
  tags: string[];
  examples: string[];
  onClick?: () => void;
}

const NicheCard: FC<NicheCardProps> = ({ image, title, description, tags, examples }) => {
  const truncated = examples.join(', ');
  const maxLength = 35;
  const displayText =
    truncated.length > maxLength ? truncated.substring(0, maxLength) + '...' : truncated;

  return (
    <Card className="rounded-xl bg-[#161616] text-white lg:px-5 lg:py-5">
      <div className="relative h-40">
        <VedioModal
          trigger={<Image src={image} alt={title} fill className="rounded-xl object-cover" />}
          title="MrBeast"
          videoId={'videoId'}
          subtitle={'“I Bought Everything In A Store”'}
          youtubeUrl={'youtubeUrl'}
        />
      </div>
      <div className="mt-4 space-y-3">
        <div className="flex flex-wrap items-center justify-between text-xs text-gray-300">
          <div className="rounded-md border border-[#BAFF381F] bg-[#2a2a2a] p-2">
            {tags.map((tag, i) => (
              <span key={i} className="rounded-md text-white">
                {tag}
                {i < tag.length - 1 && ', '}
              </span>
            ))}
          </div>
          <ExternalLink className="h-5 w-5 cursor-pointer text-white" />
        </div>

        <Text className="text-xl font-semibold">{title}</Text>
        <Text variant="base" className="text-[#AAACA6]">
          {description}
        </Text>
        <Text variant="base" className="text-[#AAACA6]">
          Examples: <span className="text-white">{displayText}</span>
        </Text>

        {/* <VedioModal
          trigger={<Button variant="green">Use this style</Button>}
          title="MrBeast"
          videoId={'videoId'}
          subtitle={'“I Bought Everything In A Store”'}
          youtubeUrl={'youtubeUrl'}
        /> */}

        <NicheStyleModal trigger={<Button variant="green">Use this style</Button>} />
      </div>
    </Card>
  );
};

export default NicheCard;
