'use client';

import { useState } from 'react';

import { Button } from 'components/ui/Button';
import Dialog from 'components/ui/Dialog';

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
      description="This section will be permanently removed from your outline. This action cannot be undone."
      footer={
        <div className="flex w-full gap-3">
          <Button variant="outline" className="flex-1" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button variant="destructive" className="flex-1" onClick={handleDelete}>
            Delete
          </Button>
        </div>
      }
    />
  );
}
