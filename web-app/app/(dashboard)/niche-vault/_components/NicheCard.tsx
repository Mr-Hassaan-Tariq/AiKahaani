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

const NicheCard: FC<NicheCardProps> = ({ id, title, description, tone, topChannels, thumbnailUrl }) => {
  const badge = tone?.[0] || null;
  const author = topChannels?.[0]?.name || null;
  const gradient = CARD_GRADIENTS[id % CARD_GRADIENTS.length];

  return (
    <div className="flex flex-col overflow-hidden rounded-xl border border-border bg-card">
      {/* Thumbnail */}
      <div className="relative w-full aspect-[16/10] overflow-hidden bg-muted">
        {thumbnailUrl ? (
          <img src={thumbnailUrl} alt={title} className="w-full h-full object-cover" />
        ) : (
          <div className={`w-full h-full bg-gradient-to-br ${gradient} flex items-center justify-center`}>
            <span className="text-white/20 text-6xl font-black select-none">{title[0]}</span>
          </div>
        )}
        {badge && (
          <span className="absolute top-3 left-3 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white/90 backdrop-blur-sm text-[#0F172A] text-xs font-semibold shadow-sm">
            {badge}
          </span>
        )}
      </div>

      {/* Content */}
      <div className="flex flex-1 flex-col gap-3 p-6">
        <h3 className="text-[18px] font-bold text-foreground leading-snug">{title}</h3>
        <p className="text-sm text-muted-foreground leading-relaxed flex-1 line-clamp-3">
          {description}
        </p>

        {/* Footer */}
        <NicheStyleModal
          trigger={
            <button className="flex items-center justify-between w-full pt-4 mt-2 border-t border-border hover:opacity-80 transition-opacity">
              {author ? (
                <span className="flex items-center gap-2 text-[13px] font-medium text-muted-foreground">
                  <span className="w-6 h-6 rounded-full bg-primary/10 text-primary text-[10px] font-bold flex items-center justify-center shrink-0">
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
