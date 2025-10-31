'use client';

import { useEffect, useState } from 'react';
import Image from 'next/image';
import { useParams, useRouter } from 'next/navigation';
import { Pin } from 'lucide-react';
import { toast } from 'sonner';

import { MicrophoneIcon, ScriptIcon, TvIcon } from '../_components/components';
import DeleteConfirmationModal from '../_components/DeleteConfirmationModal';
import ThumbnailImage from '../../../../public/images/no-niche.png';
import { deleteClientDataAction, getClientDataAction } from 'lib/utils/clientDataActions';
import Button from 'components/ui/Button';
import Card from 'components/ui/Card';

interface NicheDetailsType {
  id: number;
  title: string;
  tagline?: string;
  prompt?: string;
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

export default function NicheDetailsPage() {
  const { nicheId } = useParams();
  const router = useRouter();
  const [niche, setNiche] = useState<NicheDetailsType | null>(null);
  const [loading, setLoading] = useState(false);
  const [image, setImage] = useState<string | typeof ThumbnailImage | null>(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    const fetchNiche = async () => {
      if (!nicheId) return;
      setLoading(true);
      try {
        const res = await getClientDataAction<{ data: NicheDetailsType }>(
          `v1/admin/niches/${nicheId}/`,
        );
        setNiche(res.data);
      } catch (err: any) {
        console.error('Error fetching niche details:', err?.response || err);
        toast.error('Failed to load niche details');
      } finally {
        setLoading(false);
      }
    };
    fetchNiche();
  }, [nicheId]);

  const handleDeleteConfirm = async () => {
    if (!nicheId) {
      toast.error('Invalid niche id');
      return;
    }

    setDeleting(true);
    try {
      await deleteClientDataAction<void>(`v1/admin/niches/${nicheId}/`);
      toast.success('Niche deleted successfully');
      router.push('/niches');
    } catch (err: any) {
      console.error('Error deleting niche:', err);
      const msg = err?.message ?? 'Failed to delete niche';
      toast.error(msg);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <Card className="min-h-screen p-6 text-white lg:p-12">
      <div className="mx-auto max-w-4xl space-y-8">
        {loading ? (
          <div className="py-20 text-center text-gray-300">Loading niche details...</div>
        ) : niche ? (
          <>
            <header className="space-y-2">
              <h1 className="text-3xl font-bold">{niche.title}</h1>
              <p className="text-gray-400">
                {niche.tagline ||
                  'Engaging, anonymous, and binge-worthy. Narrate without showing your face.'}
              </p>
            </header>

            <div className="relative h-64 w-full">
              {image ? (
                <Image
                  src={image}
                  alt={niche.title}
                  className="h-48 w-full rounded-xl object-contain"
                  height={150}
                  onError={() => setImage(ThumbnailImage ?? '')}
                  width={400}
                />
              ) : (
                <div className="flex h-48 w-full items-center justify-center rounded-xl bg-[#2a2a2a] text-lg font-semibold">
                  Thumbnail
                </div>
              )}
            </div>

            {niche.prompt && (
              <section className="rounded-xl border border-[#2a2a2a] bg-[#161616] p-4">
                <h3 className="mb-2 text-xl font-semibold">Prompt</h3>
                <p className="whitespace-pre-line text-gray-300">{niche.prompt}</p>
              </section>
            )}

            {/* Script Structure */}
            <section>
              <div className="mb-2 flex items-center gap-2">
                {ScriptIcon}
                <h3 className="text-lg font-semibold">Script structure overview:</h3>
              </div>
              {niche.script_structure ? (
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
                <p className="text-sm text-gray-400">No script structure available.</p>
              )}
            </section>

            <hr className="border border-[#2a321a]" />

            {/* Tone & Pacing */}
            <section>
              <div className="mb-2 flex items-center gap-2">
                {MicrophoneIcon}
                <h3 className="text-lg font-semibold">Tone & pacing:</h3>
              </div>
              {niche.tone?.length || niche.pacing?.length ? (
                <ul className="space-y-1 text-sm">
                  {niche.tone?.map((t, i) => (
                    <li key={i}>● Tone: {t}</li>
                  ))}
                  {niche.pacing?.map((p, i) => (
                    <li key={i}>● Pacing: {p}</li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-gray-400">No tone or pacing info available.</p>
              )}
            </section>

            <hr className="border border-[#2a321a]" />

            {/* Top Channels */}
            <section>
              <div className="mb-2 flex items-center gap-2">
                {TvIcon}
                <h3 className="text-lg font-semibold">Top channels using this style:</h3>
              </div>
              {niche.top_channels?.length ? (
                <ul className="space-y-1 text-sm">
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
                <p className="text-sm text-gray-400">No channels available.</p>
              )}
            </section>

            <hr className="border border-[#2a321a]" />

            {/* Best For */}
            <section>
              <div className="mb-2 flex items-center gap-2">
                <Pin className="h-5 w-5 text-white" />
                <h3 className="text-lg font-semibold">Best for</h3>
              </div>
              {niche.best_for?.length ? (
                <div className="flex flex-wrap gap-2 text-sm">
                  {niche.best_for.map((b, i) => (
                    <span key={i} className="text-gray-200">
                      {b}
                      {i < (niche.best_for?.length ?? 0) - 1 && <span> ●</span>}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-400">No best-for data</p>
              )}
            </section>

            <div className="flex items-center gap-4 pt-8">
              <Button
                variant="green"
                onClick={() => router.push(`/niches/create?nicheId=${nicheId}`)}
                disabled={deleting}
              >
                Update this niche format
              </Button>

              <DeleteConfirmationModal
                trigger={
                  <Button variant="red" type="button" disabled={deleting}>
                    {deleting ? 'Deleting...' : 'Delete niche'}
                  </Button>
                }
                title="Delete Niche"
                description="Are you sure you want to delete this niche? This action cannot be undone."
                onConfirm={handleDeleteConfirm}
              />
            </div>
          </>
        ) : (
          <div className="text-center text-gray-400">No data found</div>
        )}
      </div>
    </Card>
  );
}
