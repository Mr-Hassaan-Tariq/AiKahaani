import Image from 'next/image';
import Link from 'next/link';
import CarouselImage from 'assets/carousel-image.jpg';

import Col from './Col';
import Row from './Row';
import Text from './Text';
import { successStories } from 'lib/localData';
import { cn } from 'lib/utils';
import ExportIcon from 'components/icons/ExportIcon';
import PlaneIcon from 'components/icons/PlaneIcon';

type SuccessStory = (typeof successStories)[number];
type SuccessStoryCardProps = {
  story: SuccessStory;
  isActive: boolean;
};

export default function SuccessStoryCard({ story, isActive }: SuccessStoryCardProps) {
  return (
    <div
      className={cn(
        'relative h-[500px] w-full transform overflow-hidden rounded-3xl border border-brand-green/10 bg-brand-black p-8 transition-all duration-500',
        isActive &&
          'scale-110 border-brand-green/30 bg-gradient-to-br from-transparent to-brand-green/5'
      )}
      style={{
        transition: 'all 500ms ease-in-out',
      }}
    >
      {/* Content */}
      <Col className="gap-5">
        {/* Header */}
        <Text variant="sm" className="font-medium text-white">
          {story.name} {story.subscribers}
        </Text>

        <Image
          // src={story.image}
          src={CarouselImage}
          alt={story.name}
          width={500}
          height={500}
          className={cn(
            'w-full rounded-2xl bg-white object-cover',
            isActive ? 'h-[240px]' : 'h-[220px]'
          )}
        />
        <Row>
          <Row className="gap-2 rounded-[8px] border border-brand-green/10 bg-white/10 p-2 shadow-[0.242px_35.999px_132px_0_rgba(255,255,255,0.04),_0.048px_7.2px_21.45px_0_rgba(255,255,255,0.02)]">
            <PlaneIcon />
            <Text variant="xs" className="text-white">
              {story.category}
            </Text>
          </Row>
          <ExportIcon className="cursor-pointer active:scale-90" />
        </Row>

        <Col className="gap-4">
          <Text variant="xl" className="text-white">
            My Secret to Consistent Uploads
          </Text>
          <Text variant="sm" className="text-[#AAACA6]">
            {story.description}
          </Text>
        </Col>

        <Link href="/about-partner">
          <button className="group flex items-center gap-2 text-sm font-medium text-white transition-colors hover:text-white/80">
            Try now
            {icon}
          </button>
        </Link>
      </Col>
    </div>
  );
}
const icon = (
  <svg
    className="h-4 w-4 transition-transform group-hover:translate-x-1"
    fill="none"
    viewBox="0 0 24 24"
    stroke="currentColor"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M17 8l4 4m0 0l-4 4m4-4H3"
    />
  </svg>
);
