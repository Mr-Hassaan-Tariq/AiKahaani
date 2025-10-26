'use client';

import { useEffect, useRef, useState } from 'react';
import Image from 'next/image';
import { Pin } from 'lucide-react';
import { toast } from 'sonner';

import { MicrophoneIcon, ScriptIcon, TvIcon } from './components';
import { getClientDataAction, postClientDataAction } from 'lib/utils/clientDataActions';
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
  const [open, setOpen] = useState(false);
  const [niche, setNiche] = useState<NicheDetailsType | null>(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    const fetchNiche = async () => {
      if (!open || !nicheId) return;
      setLoading(true);
      try {
        const res = await getClientDataAction<{ data: NicheDetailsType }>(
          `v1/admin/niches/${nicheId}/`,
        );
        setNiche(res.data);
      } catch (err: any) {
        console.error('Error fetching niche details:', err?.response || err);
      } finally {
        setLoading(false);
      }
    };
    fetchNiche();
  }, [open, nicheId]);

  // Upload button click handler
  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  // File upload handler
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !niche) return;

    try {
      setUploading(true);
      const formData = new FormData();
      formData.append('thumbnail', file);

      const response = await postClientDataAction<{ data: { thumbnail_url: string } }, FormData>(
        `v1/admin/niches/${niche.id}/upload-thumbnail/`,
        formData,
      );

      const newUrl = response?.data?.thumbnail_url;
      if (newUrl) {
        setNiche((prev) => (prev ? { ...prev, thumbnail_url: newUrl } : prev));
      }
      toast.success('Thumbnail uploaded successfully!');
    } catch (error) {
      console.error('Thumbnail upload failed:', error);
    } finally {
      setUploading(false);
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
          <Button type="submit" variant="green">
            Apply this niche format
          </Button>
        </Row>
      }
    >
      {loading ? (
        <div className="py-10 text-center text-white">Loading niche details...</div>
      ) : niche ? (
        <div className="space-y-6 text-white">
          {/* Thumbnail Section */}
          <div className="flex flex-col items-center gap-3">
            {niche?.thumbnail_url ? (
              <Image
                src={niche.thumbnail_url}
                alt={niche.title}
                className="w-full rounded-xl object-cover"
                height={150}
                width={400}
              />
            ) : (
              <div className="flex h-48 w-full items-center justify-center rounded-xl bg-[#2a2a2a] text-lg font-semibold">
                Thumbnail
              </div>
            )}

            {/* Hidden File Input */}
            <input
              type="file"
              accept="image/*"
              ref={fileInputRef}
              className="hidden"
              onChange={handleFileChange}
            />

            {/* Upload Button */}
            <Button
              onClick={handleUploadClick}
              disabled={uploading}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {uploading
                ? 'Uploading...'
                : niche?.thumbnail_url
                  ? 'Change Thumbnail'
                  : 'Upload Thumbnail'}
            </Button>
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

          {/* Tone & Pacing */}
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
