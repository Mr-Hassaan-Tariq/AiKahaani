'use client';

import { useState } from 'react';

import useToast from 'lib/utils/useToast';
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
  const toast = useToast();
  const [open, setOpen] = useState(false);

  function handleDelete() {
    // deleteProfileImage(undefined, {
    //   onSuccess: () => {
    onDelete();
    toast.success('Success', 'Deleted successfully');
    //     setOpen(false);
    //     router.refresh();
    //   },
    //   // eslint-disable-next-line @typescript-eslint/no-explicit-any
    //   onError: (error: any) => {
    //     logger.error(error);
    //     toast.error('Something went wrong', error.message?.toString());
    //   },
    // });
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
