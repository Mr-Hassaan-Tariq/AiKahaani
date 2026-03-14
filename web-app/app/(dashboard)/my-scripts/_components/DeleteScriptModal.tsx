'use client';

import { useState } from 'react';

import { useDeleteOutlineGeneration } from 'lib/hooks/useDeleteScriptGeneration';
import { Button } from 'components/ui/Button';
import Dialog from 'components/ui/Dialog';

export default function DeleteScriptModal({
  trigger,
  script,
  actions,
}: {
  trigger: React.ReactNode;
  script: any;
  actions: any;
}) {
  const [open, setOpen] = useState(false);
  const { mutate: deleteScript, isPending: isDeleting } = useDeleteOutlineGeneration();

  function handleDelete() {
    if (isDeleting) return;
    if (script.type === 'script' && script.status === 'generated') {
      deleteScript(script.uuid);
      return;
    }
    actions.onDelete?.(script.uuid);
    setOpen(false);
  }

  return (
    <Dialog
      open={open}
      setOpen={setOpen}
      trigger={trigger}
      title="Delete this script?"
      description="This action will permanently remove the script from your workspace. You won't be able to recover it."
      footer={
        <div className="flex w-full gap-3">
          <Button variant="outline" className="flex-1" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button variant="destructive" className="flex-1" onClick={handleDelete} loading={isDeleting}>
            Delete
          </Button>
        </div>
      }
    />
  );
}
