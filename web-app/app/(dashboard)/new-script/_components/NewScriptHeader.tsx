'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { Edit3 } from 'lucide-react';

import { getClientDataAction } from 'lib/utils/clientDataActions';
import Col from 'components/ui/Col';
import H3 from 'components/ui/H3';
import Text from 'components/ui/Text';

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
        console.log('Fetched niche data:', res.data);
      } catch (err: any) {
        console.error('Error fetching niche details:', err?.response || err);
        setNiche(null);
      }
    };

    fetchNiche();
  }, [searchParams]);

  return (
    <Col className="w-full items-center space-y-2 text-center">
      <H3>Create Your Script</H3>

      {niche ? (
        <div className="flex items-center gap-1 text-sm text-gray-300">
          <span>
            You’ve selected niche template:{' '}
            <span className="font-semibold text-white">{niche.title}</span>
          </span>
          <button
            type="button"
            onClick={() => console.log('Edit niche clicked')}
            className="ml-1 text-white transition-colors hover:text-[#BAFF38]"
            title="Edit selected niche"
          >
            <Edit3 size={14} strokeWidth={1.5} />
          </button>
        </div>
      ) : (
        <Text variant="lg" className="text-brand-secondary">
          Fill out the details below to generate your YouTube script
        </Text>
      )}
    </Col>
  );
}
