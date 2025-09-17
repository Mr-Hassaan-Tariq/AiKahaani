'use client';

import { useState } from 'react';

import Button from 'components/ui/Button';
import Dialog from 'components/ui/Dialog';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';

export default function DeletePhotoModal({
  trigger,
  script,
  actions,
}: {
  trigger: React.ReactNode;
  script: any;
  actions: any;
}) {
  const [open, setOpen] = useState(false);

  function handleDelete() {
    actions.onDelete?.(script.id);
    setOpen(false);
  }

  return (
    <Dialog
      open={open}
      setOpen={setOpen}
      trigger={trigger}
      title="Delete this script?"
      description="This action will permanently remove the script from your workspace. You won’t be able to recover it."
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
          <Button type="submit" variant="red" onClick={handleDelete}>
            Delete
          </Button>
        </Row>
      }
    />
  );
}
