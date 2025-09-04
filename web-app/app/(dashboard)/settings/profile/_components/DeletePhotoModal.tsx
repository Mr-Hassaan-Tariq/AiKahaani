'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

import useDeleteProfileImage from 'lib/hooks/useDeleteProfileImage';
import { logger } from 'lib/logger';
import useToast from 'lib/utils/useToast';
import Button from 'components/ui/Button';
import Dialog from 'components/ui/Dialog';
import PageLoader from 'components/ui/PageLoader';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';

export default function DeletePhotoModal({ trigger }: { trigger: React.ReactNode }) {
  const toast = useToast();
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const { isPending, mutate: deleteProfileImage } = useDeleteProfileImage();

  function handleDelete() {
    deleteProfileImage(undefined, {
      onSuccess: () => {
        toast.success('Success', 'Profile removed successfully');
        setOpen(false);
        router.refresh();
      },

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      onError: (error: any) => {
        logger.error(error);
        toast.error('Something went wrong', error.message?.toString());
      },
    });
  }

  return (
    <>
      {isPending && <PageLoader size="2xl" />}
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
            <Button type="submit" variant="red" onClick={handleDelete}>
              Remove photo
            </Button>
          </Row>
        }
      />
    </>
  );
}
