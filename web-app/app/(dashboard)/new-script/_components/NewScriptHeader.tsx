'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { Edit3 } from 'lucide-react';

import { getClientDataAction } from 'lib/utils/clientDataActions';

interface NicheDetailsType {
  id: number;
  title: string;
  tagline?: string;
  thumbnail_url?: string | null;
  script_structure?: {
    intro?: string;
    body?: string;
    conclusion?: string;
  };
  tone?: string[];
  pacing?: string[];
  top_channels?: { name: string; link: string }[];
  best_for?: string[];
}

export default function NewScriptHeader() {
  const searchParams = useSearchParams();
  const [niche, setNiche] = useState<NicheDetailsType | null>(null);

  useEffect(() => {
    const nicheId = searchParams ? searchParams.get('nicheId') : null;
    if (!nicheId) return;

    const fetchNiche = async () => {
      try {
        const res = await getClientDataAction<{ data: NicheDetailsType }>(
          `auth/niches/${nicheId}/`,
        );
        setNiche(res.data);
      } catch (err: any) {
        console.error('Error fetching niche details:', err?.response || err);
        setNiche(null);
      }
    };

    fetchNiche();
  }, [searchParams]);

  return (
    <div className="flex w-full flex-col items-center gap-2 text-center">
      <h2 className="text-2xl font-bold text-foreground">Create Your Script</h2>

      {niche ? (
        <div className="flex items-center gap-1 text-sm text-muted-foreground">
          <span>
            You&apos;ve selected niche template:{' '}
            <span className="font-semibold text-foreground">{niche.title}</span>
          </span>
          <button
            type="button"
            onClick={() => console.log('Edit niche clicked')}
            className="ml-1 text-muted-foreground transition-colors hover:text-foreground"
            title="Edit selected niche"
          >
            <Edit3 size={14} strokeWidth={1.5} />
          </button>
        </div>
      ) : (
        <p className="text-sm text-muted-foreground">
          Fill out the details below to generate your YouTube script
        </p>
      )}
    </div>
  );
}
