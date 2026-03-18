'use client';

import { useEffect, useState } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { Mic, Pin, Settings2, Tv } from 'lucide-react';

import ThumbnailImage from '../../../../public/images/no-niche.png';
import { getClientDataAction } from 'lib/utils/clientDataActions';
import Button from 'components/ui/Button';
import Dialog from 'components/ui/Dialog';
import Spinner from 'components/ui/Spinner';

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
        <Button onClick={handleApply} disabled={loading || !niche?.id}>
          Apply this niche format
        </Button>
      }
    >
      {loading ? (
        <div className="flex items-center justify-center py-10">
          <Spinner size="md" color="primary" />
        </div>
      ) : niche ? (
        <div className="space-y-5">
          {/* Thumbnail */}
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
              <div className="flex h-48 w-full items-center justify-center rounded-xl border border-border bg-muted text-sm font-medium text-muted-foreground">
                No thumbnail
              </div>
            )}
          </div>

          {/* Script Structure */}
          <section>
            <div className="mb-2 flex items-center gap-2 text-foreground">
              <Settings2 className="h-4 w-4 text-muted-foreground" />
              <h3 className="text-sm font-semibold">Script structure overview</h3>
            </div>
            {niche?.script_structure ? (
              <ul className="space-y-1.5 pl-1 text-sm text-muted-foreground">
                {niche.script_structure.intro && (
                  <li>
                    <span className="font-medium text-foreground">Intro:</span>{' '}
                    {niche.script_structure.intro}
                  </li>
                )}
                {niche.script_structure.body && (
                  <li>
                    <span className="font-medium text-foreground">Body:</span>{' '}
                    {niche.script_structure.body}
                  </li>
                )}
                {niche.script_structure.conclusion && (
                  <li>
                    <span className="font-medium text-foreground">Conclusion:</span>{' '}
                    {niche.script_structure.conclusion}
                  </li>
                )}
              </ul>
            ) : (
              <p className="pl-1 text-sm text-muted-foreground">No script structure available.</p>
            )}
          </section>

          <hr className="border-border" />

          {/* Tone & Pacing */}
          <section>
            <div className="mb-2 flex items-center gap-2">
              <Mic className="h-4 w-4 text-muted-foreground" />
              <h3 className="text-sm font-semibold text-foreground">Tone &amp; pacing</h3>
            </div>
            {niche?.tone?.length || niche?.pacing?.length ? (
              <ul className="space-y-1 pl-1 text-sm text-muted-foreground">
                {niche.tone?.map((t, i) => (
                  <li key={`tone-${i}`}>
                    <span className="font-medium text-foreground">Tone:</span> {t}
                  </li>
                ))}
                {niche.pacing?.map((p, i) => (
                  <li key={`pacing-${i}`}>
                    <span className="font-medium text-foreground">Pacing:</span> {p}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="pl-1 text-sm text-muted-foreground">
                No tone or pacing info available.
              </p>
            )}
          </section>

          <hr className="border-border" />

          {/* Top Channels */}
          <section>
            <div className="mb-2 flex items-center gap-2">
              <Tv className="h-4 w-4 text-muted-foreground" />
              <h3 className="text-sm font-semibold text-foreground">
                Top channels using this style
              </h3>
            </div>
            {niche?.top_channels?.length ? (
              <ul className="space-y-1 pl-1 text-sm">
                {niche.top_channels.map((ch, i) => (
                  <li key={i}>
                    <a
                      href={ch.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary hover:underline"
                    >
                      @{ch.name}
                    </a>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="pl-1 text-sm text-muted-foreground">No channels available.</p>
            )}
          </section>

          <hr className="border-border" />

          {/* Best For */}
          <section>
            <div className="mb-2 flex items-center gap-2">
              <Pin className="h-4 w-4 text-muted-foreground" />
              <h3 className="text-sm font-semibold text-foreground">Best for</h3>
            </div>
            {niche?.best_for?.length ? (
              <div className="flex flex-wrap gap-1.5">
                {niche.best_for.map((b, i) => (
                  <span
                    key={i}
                    className="rounded-md border border-border bg-accent px-2.5 py-1 text-xs text-foreground"
                  >
                    {b}
                  </span>
                ))}
              </div>
            ) : (
              <p className="pl-1 text-sm text-muted-foreground">No best-for data.</p>
            )}
          </section>
        </div>
      ) : (
        <div className="py-10 text-center text-sm text-muted-foreground">No data found.</div>
      )}
    </Dialog>
  );
}
