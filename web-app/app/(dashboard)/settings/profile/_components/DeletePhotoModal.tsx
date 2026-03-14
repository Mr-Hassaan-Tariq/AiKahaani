'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

import useDeleteProfileImage from 'lib/hooks/useDeleteProfileImage';
import { logger } from 'lib/logger';
import useToast from 'lib/utils/useToast';
import { Button } from 'components/ui/Button';
import Dialog from 'components/ui/Dialog';

export default function DeletePhotoModal({ trigger }: { trigger: React.ReactNode }) {
  const toast = useToast();
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const { isPending, mutate: deleteProfileImage } = useDeleteProfileImage();

  function handleDelete() {
    deleteProfileImage(undefined, {
      onSuccess: () => {
        toast.success('Success', 'Profile photo removed');
        setOpen(false);
        router.refresh();
      },
      onError: (error: any) => {
        logger.error(error);
        toast.error('Something went wrong', error.message?.toString());
      },
    });
  }

  return (
    <Dialog
      open={open}
      setOpen={setOpen}
      trigger={trigger}
      title="Remove profile photo?"
      description="Your initials will be shown instead. This action cannot be undone."
      footer={
        <div className="flex w-full gap-3">
          <Button variant="outline" className="flex-1" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button variant="destructive" className="flex-1" loading={isPending} onClick={handleDelete}>
            Remove photo
          </Button>
        </div>
      }
    />
  );
}
