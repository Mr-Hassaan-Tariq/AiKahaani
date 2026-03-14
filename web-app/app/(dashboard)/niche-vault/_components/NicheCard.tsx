'use client';

import { FC, useState } from 'react';
import Image from 'next/image';

import ThumbnailImage from '../../../../public/images/no-niche.png';
import NicheStyleModal from './NicheStyleModal';
import VedioModal from './VedioModal';
import { Button } from 'components/ui/Button';

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
  const [imagePresent, setImagePresent] = useState(!!thumbnailUrl);
  const [imageError, setImageError] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);

  const tags = [...(tone || []), ...(pacing || [])].slice(0, 4);
  const examples = topChannels?.map((c) => c.name) || [];
  const videoUrl = topChannels[0]?.link || '';
  const displayExamples = examples.join(', ');
  const truncatedExamples =
    displayExamples.length > 40 ? displayExamples.substring(0, 40) + '…' : displayExamples;

  const handleImageLoad = () => { setImageLoaded(true); setImageError(false); };
  const handleImageError = () => { if (!imageLoaded) { setImageError(true); setImagePresent(false); } };

  return (
    <div className="flex flex-col overflow-hidden rounded-xl border border-border bg-card">
      {/* Thumbnail */}
      <div className="relative h-40 bg-muted">
        {imagePresent && !imageError ? (
          <VedioModal
            trigger={
              <Image
                src={thumbnailUrl || ''}
                alt={title}
                fill
                className="object-cover"
                sizes="(max-width: 768px) 100vw, 33vw"
                unoptimized
                onLoad={handleImageLoad}
                onError={handleImageError}
              />
            }
            title={title}
            videoId="videoId"
            subtitle={description}
            youtubeUrl={videoUrl}
            thumbnailUrl={thumbnailUrl || ''}
          />
        ) : (
          <Image
            src={ThumbnailImage}
            alt="placeholder"
            fill
            className="object-cover opacity-60"
            sizes="(max-width: 768px) 100vw, 33vw"
          />
        )}
      </div>

      {/* Body */}
      <div className="flex flex-1 flex-col gap-3 p-4">
        {/* Tags */}
        {tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {tags.map((tag, i) => (
              <span
                key={i}
                className="rounded-md border border-border bg-accent px-2 py-0.5 text-[10px] font-medium text-muted-foreground"
              >
                {tag}
              </span>
            ))}
          </div>
        )}

        {/* Title + description */}
        <div>
          <h3 className="text-sm font-semibold text-foreground">{title}</h3>
          <p className="mt-1 text-xs text-muted-foreground">
            {description.length > 80 ? description.slice(0, 80) + '…' : description}
          </p>
        </div>

        {/* Examples */}
        {examples.length > 0 && (
          <p className="text-xs text-muted-foreground">
            Examples: <span className="text-foreground">{truncatedExamples}</span>
          </p>
        )}

        {/* CTA */}
        <NicheStyleModal
          trigger={
            <Button size="sm" className="mt-auto w-full">
              Use this style
            </Button>
          }
          nicheId={id}
        />
      </div>
    </div>
  );
};

export default NicheCard;
