'use client';

import { useState } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';

import { VideoIcon } from './components';
import Button from 'components/ui/Button';
import Dialog from 'components/ui/Dialog';

interface VedioModalProps {
  trigger: React.ReactNode;
  title: string;
  subtitle: string;
  videoId: string;
  youtubeUrl: string;
  thumbnailUrl: string;
}

export default function VedioModal({
  trigger,
  title,
  subtitle,
  youtubeUrl,
  thumbnailUrl,
}: VedioModalProps) {
  const router = useRouter();
  const [open, setOpen] = useState(false);

  console.log('youtubeUrl............', youtubeUrl);

  return (
    <Dialog
      open={open}
      setOpen={setOpen}
      trigger={trigger}
      title={title}
      description={subtitle}
      footer={<Button onClick={() => router.push(youtubeUrl)}>{VideoIcon} Watch on YouTube</Button>}
    >
      <div className="relative mt-4 aspect-video w-full overflow-hidden rounded-xl">
        <Image src={thumbnailUrl} alt={title} fill className="rounded-xl" />
      </div>
    </Dialog>
  );
}
