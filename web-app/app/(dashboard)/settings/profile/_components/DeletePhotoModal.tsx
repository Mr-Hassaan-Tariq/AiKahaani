'use client';

import { useState } from 'react';

import Button from 'components/ui/Button';
import Dialog from 'components/ui/Dialog';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';

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
          <Button variant="gray" onClick={() => setOpen(false)}>
            <Text
              variant="base"
              className="font-extrabold [font-feature-settings:'liga'_off,'clig'_off]"
            >
              Cancel
            </Text>
          </Button>
          <Button type="submit" variant="red">
            Remove photo
          </Button>
        </Row>
      }
    />
  );
}
