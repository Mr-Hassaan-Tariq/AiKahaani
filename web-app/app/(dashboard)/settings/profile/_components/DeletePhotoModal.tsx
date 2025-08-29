'use client';

import { useState } from 'react';

import Dialog from 'components/ui/Dialog';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';
import { Button } from 'components/shadcn_ui/button';

export default function DeletePhotoModal({ trigger }: { trigger: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  return (
    <Dialog
      open={open}
      setOpen={setOpen}
      trigger={trigger}
      title="Delete profile photo?"
      description="Are you sure you want to remove your current profile photo? Your initials will be shown
          instead."
      footer={
        <Row className="w-full gap-6">
          <Button
            className="h-[52px] w-full rounded-full bg-white/10 backdrop-blur-[2px] hover:bg-white/10 hover:opacity-70"
            onClick={() => setOpen(false)}
          >
            <Text
              variant="base"
              className="font-extrabold [font-feature-settings:'liga'_off,'clig'_off]"
            >
              Cancel
            </Text>
          </Button>
          <Button
            type="submit"
            className="h-[52px] w-full rounded-full bg-error hover:bg-error hover:opacity-70"
          >
            <Text
              variant="base"
              className="font-extrabold text-[#0E0F0C] [font-feature-settings:'liga'_off,'clig'_off]"
            >
              Remove photo
            </Text>
          </Button>
        </Row>
      }
    />
  );
}
