'use client';

import { useState } from 'react';

import Button from 'components/ui/Button';
import Dialog from 'components/ui/Dialog';
import Row from 'components/ui/Row';

interface DeleteConfirmationModalProps {
  trigger: React.ReactNode;
  title?: string;
  description?: string;
  onConfirm: () => void;
}

export default function DeleteConfirmationModal({
  trigger,
  title = 'Delete Niche',
  description = 'Are you sure you want to delete this niche? This action cannot be undone.',
  onConfirm,
}: DeleteConfirmationModalProps) {
  const [open, setOpen] = useState(false);

  return (
    <Dialog
      open={open}
      setOpen={setOpen}
      trigger={trigger}
      title={title}
      description={description}
      footer={
        <Row className="w-full justify-end gap-4">
          <Button variant="gray" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button
            variant="red"
            onClick={() => {
              onConfirm();
              setOpen(false);
            }}
          >
            Yes, Delete
          </Button>
        </Row>
      }
    ></Dialog>
  );
}
