'use client';

import { useEffect, useState } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { Pin } from 'lucide-react';

import ThumbnailImage from '../../../../public/images/no-niche.png';
import { MicrophoneIcon, ScriptIcon, TvIcon } from './components';
import { getClientDataAction } from 'lib/utils/clientDataActions';
import Button from 'components/ui/Button';
import Dialog from 'components/ui/Dialog';
import Row from 'components/ui/Row';

interface FilterModalProps {
  trigger: React.ReactNode;
  nicheId: string | number;
}

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

export default function NicheStyleModal({ trigger, nicheId }: FilterModalProps) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [niche, setNiche] = useState<NicheDetailsType | null>(null);
  const [loading, setLoading] = useState(false);

  const [image, setImage] = useState<string | typeof ThumbnailImage | null>(null);
  const [imageError, setImageError] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);

  useEffect(() => {
    setImage(niche?.thumbnail_url ?? (ThumbnailImage as unknown as string));
    setImageError(false);
    setImageLoaded(false);
  }, [niche]);

  useEffect(() => {
    const fetchNiche = async () => {
      if (!open || !nicheId) return;
      setLoading(true);
      try {
        const res = await getClientDataAction<{ data: NicheDetailsType }>(
          `auth/niches/${nicheId}/`,
        );
        setNiche(res.data);
      } catch (err: any) {
        console.error('Error fetching niche details:', err?.response || err);
        setNiche(null);
      } finally {
        setLoading(false);
      }
    };
    fetchNiche();
  }, [open, nicheId]);

  const handleApply = () => {
    if (!niche?.id) return;
    setOpen(false);
    router.push(`/new-script?nicheId=${niche.id}`);
  };

  const handleImageLoad = () => {
    setImageLoaded(true);
    setImageError(false);
  };

  const handleImageError = () => {
    // Only show placeholder if image truly failed to load
    if (!imageLoaded) {
      setImageError(true);
      setImage(ThumbnailImage as unknown as string);
    }
  };

  return (
    <Dialog
      open={open}
      setOpen={setOpen}
      trigger={trigger}
      title={niche?.title || 'Niche Style'}
      description={
        niche?.tagline ||
        'Engaging, anonymous, and binge-worthy. Narrate without showing your face.'
      }
      footer={
        <Row className="w-full gap-6">
          <Button
            type="button"
            variant="green"
            onClick={handleApply}
            disabled={loading || !niche?.id}
          >
            Apply this niche format
          </Button>
        </Row>
      }
    >
      {loading ? (
        <div className="py-10 text-center text-white">Loading niche details...</div>
      ) : niche ? (
        <div className="space-y-6 text-white">
          <div className="flex flex-col gap-3">
            {image && !imageError ? (
              <div className="relative h-48 w-full overflow-hidden rounded-xl">
                <Image
                  src={image}
                  alt={niche.title}
                  fill
                  className="rounded-xl object-cover"
                  unoptimized
                  onLoad={handleImageLoad}
                  onError={handleImageError}
                />
              </div>
            ) : (
              <div className="flex h-48 w-full items-center justify-center rounded-xl bg-[#2a2a2a] text-lg font-semibold">
                Thumbnail
              </div>
            )}
          </div>

          {/* Script Structure */}
          <section className="mt-4">
            <div className="mb-2 flex items-center gap-2">
              {ScriptIcon}
              <h3 className="text-lg font-semibold">Script structure overview:</h3>
            </div>
            {niche?.script_structure ? (
              <ul className="space-y-1 pl-1 text-sm">
                {niche.script_structure.intro && (
                  <li>
                    ● <strong>Intro:</strong> {niche.script_structure.intro}
                  </li>
                )}
                {niche.script_structure.body && (
                  <li>
                    ● <strong>Body:</strong> {niche.script_structure.body}
                  </li>
                )}
                {niche.script_structure.conclusion && (
                  <li>
                    ● <strong>Conclusion:</strong> {niche.script_structure.conclusion}
                  </li>
                )}
              </ul>
            ) : (
              <p className="pl-1 text-sm text-gray-400">No script structure available.</p>
            )}
          </section>

          <hr className="border border-[#2a321a]" />

          <section>
            <div className="mb-2 flex items-center gap-2">
              {MicrophoneIcon}
              <h3 className="text-lg font-semibold">Tone & pacing:</h3>
            </div>
            {niche?.tone?.length || niche?.pacing?.length ? (
              <ul className="space-y-1 pl-1 text-sm">
                {niche.tone?.map((t, i) => (
                  <li key={`tone-${i}`}>● Tone: {t}</li>
                ))}
                {niche.pacing?.map((p, i) => (
                  <li key={`pacing-${i}`}>● Pacing: {p}</li>
                ))}
              </ul>
            ) : (
              <p className="pl-1 text-sm text-gray-400">No tone or pacing info available.</p>
            )}
          </section>

          <hr className="border border-[#2a321a]" />

          {/* Top Channels */}
          <section>
            <div className="mb-2 flex items-center gap-2">
              {TvIcon}
              <h3 className="text-lg font-semibold">Top channels using this style:</h3>
            </div>
            {niche?.top_channels?.length ? (
              <ul className="space-y-1 pl-1 text-sm">
                {niche.top_channels.map((ch, i) => (
                  <li key={i}>
                    ●{' '}
                    <a
                      href={ch.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-white hover:underline"
                    >
                      @{ch.name}
                    </a>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="pl-1 text-sm text-gray-400">No channels available.</p>
            )}
          </section>

          <hr className="border border-[#2a321a]" />

          {/* Best For */}
          <section>
            <div className="mb-2 flex items-center gap-2">
              <Pin className="h-5 w-5 text-white" />
              <h3 className="text-lg font-semibold">Best for</h3>
            </div>
            {niche?.best_for?.length ? (
              <div className="flex flex-wrap gap-2 text-sm">
                {niche?.best_for.map((b, i) => (
                  <span key={i} className="text-gray-200">
                    {b}
                    {i < (niche.best_for?.length ?? 0) - 1 && <span> ●</span>}
                  </span>
                ))}
              </div>
            ) : (
              <p className="pl-1 text-sm text-gray-400">No best-for data</p>
            )}
          </section>
        </div>
      ) : (
        <div className="text-center text-gray-400">No data found</div>
      )}
    </Dialog>
  );
}
