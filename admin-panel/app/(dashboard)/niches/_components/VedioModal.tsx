'use client';

import { useState } from 'react';

import { VideoIcon } from './components';
import Button from 'components/ui/Button';
import Dialog from 'components/ui/Dialog';

interface VedioModalProps {
  trigger: React.ReactNode;
  title: string;
  subtitle: string;
  videoId: string;
  youtubeUrl: string;
}

export default function VedioModal({ trigger, title, subtitle }: VedioModalProps) {
  const [open, setOpen] = useState(false);

  return (
    <Dialog
      open={open}
      setOpen={setOpen}
      trigger={trigger}
      title={title}
      description={subtitle}
      footer={
        <Button type="submit" variant="green">
          {VideoIcon} Watch on YouTube
        </Button>
      }
    >
      <div className="mt-4 aspect-video w-full overflow-hidden rounded-xl">
        <iframe
          src={'https://www.youtube.com/watch?v=uiBIkQlJ3pA&list=RDggNHDf18R1E&index=2'}
          title={title}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          className="h-full w-full"
        />
      </div>
    </Dialog>
  );
}
