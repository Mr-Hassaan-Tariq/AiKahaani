'use client';

import { useState } from 'react';

import Button from 'components/ui/Button';
import Dialog from 'components/ui/Dialog';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';

export default function DeleteOutlineSection({
  onDelete,
  trigger,
}: {
  onDelete: () => void;
  trigger: React.ReactNode;
}) {
  const [open, setOpen] = useState(false);

  function handleDelete() {
    onDelete();
    setOpen(false);
  }

  return (
    <Dialog
      open={open}
      setOpen={setOpen}
      trigger={trigger}
      title="Delete this section?"
      description="This section will be permanently removed from your outline. Are you sure you want to continue?"
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
