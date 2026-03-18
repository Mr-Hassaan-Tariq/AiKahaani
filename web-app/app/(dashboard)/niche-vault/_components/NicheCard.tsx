'use client';

import { FC } from 'react';
import { ArrowRight } from 'lucide-react';

import NicheStyleModal from './NicheStyleModal';

interface NicheCardProps {
  id: number;
  title: string;
  description: string;
  tone: string[];
  pacing: string[];
  topChannels: { name: string; link: string }[];
  thumbnailUrl?: string | null;
}

const CARD_GRADIENTS = [
  'from-violet-800 to-purple-600',
  'from-blue-800 to-sky-600',
  'from-emerald-800 to-teal-600',
  'from-rose-800 to-red-600',
  'from-amber-800 to-orange-600',
  'from-indigo-800 to-blue-600',
  'from-pink-800 to-rose-600',
  'from-cyan-800 to-blue-600',
  'from-slate-700 to-slate-500',
];

const NicheCard: FC<NicheCardProps> = ({
  id,
  title,
  description,
  tone,
  topChannels,
  thumbnailUrl,
}) => {
  const badge = tone?.[0] || null;
  const author = topChannels?.[0]?.name || null;
  const gradient = CARD_GRADIENTS[id % CARD_GRADIENTS.length];

  return (
    <div className="flex flex-col overflow-hidden rounded-xl border border-border bg-card">
      {/* Thumbnail */}
      <div className="relative aspect-[16/10] w-full overflow-hidden bg-muted">
        {thumbnailUrl ? (
          <img src={thumbnailUrl} alt={title} className="h-full w-full object-cover" />
        ) : (
          <div
            className={`h-full w-full bg-gradient-to-br ${gradient} flex items-center justify-center`}
          >
            <span className="select-none text-6xl font-black text-white/20">{title[0]}</span>
          </div>
        )}
        {badge && (
          <span className="absolute left-3 top-3 inline-flex items-center gap-1.5 rounded-full bg-white/90 px-2.5 py-1 text-xs font-semibold text-[#0F172A] shadow-sm backdrop-blur-sm">
            {badge}
          </span>
        )}
      </div>

      {/* Content */}
      <div className="flex flex-1 flex-col gap-3 p-6">
        <h3 className="text-[18px] font-bold leading-snug text-foreground">{title}</h3>
        <p className="line-clamp-3 flex-1 text-sm leading-relaxed text-muted-foreground">
          {description}
        </p>

        {/* Footer */}
        <NicheStyleModal
          trigger={
            <button className="mt-2 flex w-full items-center justify-between border-t border-border pt-4 transition-opacity hover:opacity-80">
              {author ? (
                <span className="flex items-center gap-2 text-[13px] font-medium text-muted-foreground">
                  <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/10 text-[10px] font-bold text-primary">
                    {author[0]}
                  </span>
                  {author}
                </span>
              ) : (
                <span />
              )}
              <ArrowRight className="h-4 w-4 text-foreground" />
            </button>
          }
          nicheId={id}
        />
      </div>
    </div>
  );
};

export default NicheCard;
