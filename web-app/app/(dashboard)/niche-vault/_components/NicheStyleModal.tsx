'use client';

import { useState } from 'react';
import Image from 'next/image';
import VedioImg from '@assets/vedioImg.png';
import { Pin } from 'lucide-react';

import { MicrophoneIcon, ScriptIcon, TvIcon } from './components';
import Button from 'components/ui/Button';
import Dialog from 'components/ui/Dialog';
import Row from 'components/ui/Row';

interface FilterModalProps {
  trigger: React.ReactNode;
}

export default function NicheStyleModal({ trigger }: FilterModalProps) {
  const [open, setOpen] = useState(false);

  return (
    <Dialog
      open={open}
      setOpen={(value) => setOpen(value)}
      trigger={trigger}
      title="Faceless Storytelling"
      description="Engaging, anonymous, and binge-worthy. <br /> Narrate without showing your face."
      footer={
        <Row className="w-full gap-6">
          <Button type="submit" variant="green">
            Apply this niche format
          </Button>
        </Row>
      }
    >
      <div className="space-y-6 text-white">
        <div className="relative mt-3 overflow-hidden rounded-xl">
          <Image
            src={VedioImg}
            alt="Faceless Storytelling"
            className="w-full rounded-xl object-cover"
            height={10}
            width={200}
          />
        </div>

        {/* Script Structure */}
        <section className="mt-4">
          <div className="mb-2 flex items-center gap-2">
            {ScriptIcon}
            <h3 className="text-lg font-semibold">Script structure overview:</h3>
          </div>
          <ul className="space-y-1 pl-1 text-sm">
            <li>
              ● <strong>Hook:</strong> Intriguing fact or provocative question
            </li>
            <li>
              ● <strong>Build-up:</strong> Gradual reveal with suspense or curiosity
            </li>
            <li>
              ● <strong>Climax:</strong> Emotional or surprising twist
            </li>
            <li>
              ● <strong>Wrap-up:</strong> Key takeaway or call to action
            </li>
          </ul>
        </section>
        <hr className="border border-[#2a321a]" />
        {/* Tone & Pacing */}
        <section className="">
          <div className="mb-2 flex items-center gap-2">
            {MicrophoneIcon}
            <h3 className="text-lg font-semibold">Tone & pacing:</h3>
          </div>
          <ul className="space-y-1 pl-1 text-sm">
            <li>● Neutral or dramatic narration</li>
            <li>
              ● <strong>Pacing:</strong> Steady build-up, often with cliffhangers
            </li>
            <li>● Written for text-to-speech or third-party narration</li>
          </ul>
        </section>
        <hr className="border border-[#2a321a]" />

        {/* Top Channels */}
        <section className="">
          <div className="mb-2 flex items-center gap-2">
            {TvIcon}
            <h3 className="text-lg font-semibold">Top channels using this style:</h3>
          </div>
          <ul className="space-y-1 pl-1 text-sm">
            <li>● @The Infographics Show</li>
            <li>● @Hook</li>
            <li>● @WatchData</li>
          </ul>
        </section>
        <hr className="border border-[#2a321a]" />

        {/* Best For */}
        <section className="">
          <div className="mb-2 flex items-center gap-2">
            <Pin className="h-5 w-5 text-white" />
            <h3 className="text-lg font-semibold">Best for</h3>
          </div>
          <div className="flex flex-wrap gap-2 text-sm">
            <span> Education</span>
            <span> ●</span>
            <span> Psychology</span>
            <span> ●</span>
            <span> Crime & Mystery</span>
            <span> ●</span>
            <span> Top 10s</span>
          </div>
        </section>
      </div>
    </Dialog>
  );
}
