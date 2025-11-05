'use client';

import { Dispatch, SetStateAction, useState } from 'react';

import Button from 'components/ui/Button';
import Dialog from 'components/ui/Dialog';
import Row from 'components/ui/Row';

interface DeleteConfirmationModalProps {
  trigger: React.ReactNode;
  title?: string;
  description?: string;
  onConfirm: () => void;
  open?: boolean;
  setOpen?: Dispatch<SetStateAction<boolean>>;
}

export default function DeleteConfirmationModal({
  trigger,
  title = 'Delete Niche',
  description = 'Are you sure you want to delete this niche? This action cannot be undone.',
  onConfirm,
  open: controlledOpen,
  setOpen: controlledSetOpen,
}: DeleteConfirmationModalProps) {
  const [internalOpen, setInternalOpen] = useState(false);
  const open = controlledOpen !== undefined ? controlledOpen : internalOpen;
  const setOpen = controlledSetOpen || setInternalOpen;

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
