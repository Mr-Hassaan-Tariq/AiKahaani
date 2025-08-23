'use client';

import React, { useEffect, useState } from 'react';

interface CarouselProps {
  items?: React.ReactNode[];
  className?: string;
  autoPlay?: boolean;
  interval?: number;
}

export default function Carousel({
  items = [],
  className = '',
  autoPlay = true,
  interval = 5000,
}: CarouselProps) {
  const [currentIndex, setCurrentIndex] = useState(0);

  const handleDotClick = (index: number) => {
    setCurrentIndex(index);
  };

  const nextSlide = () => {
    setCurrentIndex((prev) => (prev + 1) % items.length);
  };

  const prevSlide = () => {
    setCurrentIndex((prev) => (prev - 1 + items.length) % items.length);
  };

  // Auto-play functionality
  useEffect(() => {
    if (!autoPlay || items.length <= 1) return;

    const timer = setInterval(() => {
      nextSlide();
    }, interval);

    return () => clearInterval(timer);
  }, [currentIndex, autoPlay, interval, items.length]);

  if (items.length === 0) return null;

  return (
    <div className={`w-full ${className}`}>
      {/* Carousel Content */}
      <div className="relative w-full overflow-hidden rounded-xl">
        <div
          className="flex transition-transform duration-700 ease-out"
          style={{
            transform: `translateX(-${currentIndex * 100}%)`,
          }}
        >
          {items.map((item, index) => (
            <div key={index} className="w-full flex-shrink-0" style={{ minWidth: '100%' }}>
              <div className="h-full w-full px-2">{item}</div>
            </div>
          ))}
        </div>

        {/* Navigation Arrows */}
        {items.length > 1 && (
          <>
            <button
              onClick={prevSlide}
              className="absolute left-2 top-1/2 z-10 flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-full bg-black/50 text-white backdrop-blur-sm transition-all duration-200 hover:scale-110 hover:bg-black/70"
              aria-label="Previous slide"
            >
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 19l-7-7 7-7"
                />
              </svg>
            </button>
            <button
              onClick={nextSlide}
              className="absolute right-2 top-1/2 z-10 flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-full bg-black/50 text-white backdrop-blur-sm transition-all duration-200 hover:scale-110 hover:bg-black/70"
              aria-label="Next slide"
            >
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </button>
          </>
        )}
      </div>

      {/* Dots/Pagination */}
      <div className="mt-8 flex justify-center gap-3">
        {items.map((_, index) => (
          <button
            key={index}
            onClick={() => handleDotClick(index)}
            className={`group relative transition-all duration-300 ease-out ${
              index === currentIndex
                ? 'h-2 w-8 rounded-full bg-green-500'
                : 'h-2 w-2 rounded-full bg-gray-600 hover:bg-gray-500'
            }`}
            aria-label={`Go to slide ${index + 1}`}
          >
            {/* Ripple effect on click */}
            <span
              className={`absolute inset-0 rounded-full transition-all duration-300 ${
                index === currentIndex ? 'scale-150 bg-green-400/20' : 'scale-100 bg-transparent'
              }`}
            />
          </button>
        ))}
      </div>
    </div>
  );
}
