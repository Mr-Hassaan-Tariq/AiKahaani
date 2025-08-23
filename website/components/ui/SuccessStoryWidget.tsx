'use client';

import { useState } from 'react';

import SuccessStoryCard from './SuccessStoryCard';
import { successStories } from 'lib/localData';
import { cn } from 'lib/utils';
import Col from 'components/ui/Col';
import Text from 'components/ui/Text';
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from 'components/shadcn_ui/carousel';

export default function SuccessStoryWidget({ id }: { id?: string }) {
  return (
    <Col id={id} className="bg-black pb-10 font-figtree lg:gap-16 lg:pb-20">
      {/* heading */}
      <Col className="gap-4">
        <div className="mx-auto max-w-xl text-center">
          <Text className="text-2xl text-white md:text-3xl lg:text-5xl">
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
        <CarouselContent className="h-[450px] items-center gap-8 lg:h-[600px]">
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

const carouselClasses =
  'top-0 z-50 size-[52px] rounded-full border-none bg-white/10 text-white transition-all duration-300 hover:bg-white/10 hover:text-white/60 active:scale-90';
