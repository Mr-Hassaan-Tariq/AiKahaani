'use client';

import { useState } from 'react';
import Image from 'next/image';

import { successStories } from 'lib/localData';
import { cn } from 'lib/utils';
import Col from 'components/ui/Col';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';
import ExportIcon from 'components/icons/ExportIcon';
import PlaneIcon from 'components/icons/PlaneIcon';
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from 'components/shadcn_ui/carousel';

export default function SuccessStoryWidget() {
  return (
    <Col className="gap-16 bg-black pb-20 font-figtree">
      {/* heading */}
      <Col className="gap-4">
        <div className="mx-auto max-w-xl text-center">
          <Text variant="5xl" className="text-white">
            Success stories powered by TubeGenius
          </Text>
        </div>
        <Text variant="lg" className="mx-auto max-w-2xl text-center text-[#AAACA6]">
          See how real creators turn ideas into videos — and what they say about the process.
        </Text>
      </Col>

      {/* Carousel */}
      <CarouselWidget />
    </Col>
  );
}

type SuccessStory = (typeof successStories)[number];

function CarouselWidget() {
  const [activeIndex, setActiveIndex] = useState(1);

  return (
    <div className="relative mx-auto w-full overflow-hidden">
      <Carousel
        className="w-full"
        opts={{
          align: 'center',
          containScroll: false,
          startIndex: 1,
        }}
        setApi={(api) => {
          if (api) {
            api.on('select', () => {
              setActiveIndex(api.selectedScrollSnap());
            });
          }
        }}
      >
        <CarouselContent className="h-[600px] items-center gap-8">
          {successStories.map((story, index) => (
            <CarouselItem
              key={story.id}
              defaultChecked={index === 1}
              className="flex basis-full items-center md:basis-1/2 md:pl-4 lg:basis-1/3"
            >
              <SuccessStoryCard story={story} isActive={index === activeIndex} />
            </CarouselItem>
          ))}
        </CarouselContent>

        {/* Navigation */}
        <div className="mt-12 flex items-center justify-center gap-4">
          <CarouselPrevious className={cn('relative left-0 translate-y-0', carouselClasses)} />
          <CarouselNext className={cn('relative right-0 translate-y-0', carouselClasses)} />
        </div>
      </Carousel>
    </div>
  );
}

function SuccessStoryCard({ story, isActive }: { story: SuccessStory; isActive: boolean }) {
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
          src={story.image}
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

        <button className="group flex items-center gap-2 text-sm font-medium text-white transition-colors hover:text-white/80">
          Try now
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
        </button>
      </Col>
    </div>
  );
}

const carouselClasses =
  'top-0 z-50 size-[52px] rounded-full border-none bg-white/10 text-white transition-all duration-300 hover:bg-white/10 hover:text-white/60 active:scale-90';
