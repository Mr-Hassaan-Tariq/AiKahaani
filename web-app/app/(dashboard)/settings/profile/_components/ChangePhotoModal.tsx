'use client';

import { ReactNode, useState } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { ImagePlus } from 'lucide-react';

import useUpdateProfileImage from 'lib/hooks/useUpdateProfileImage';
import { logger } from 'lib/logger';
import useToast from 'lib/utils/useToast';
import { Button } from 'components/ui/Button';
import Dialog from 'components/ui/Dialog';

export default function ChangePhotoModal({ trigger }: { trigger: ReactNode }) {
  const toast = useToast();
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [image, setImage] = useState<File | undefined>();
  const { isPending, mutate: updateProfileImage } = useUpdateProfileImage();

  function handleSave() {
    if (!image) return toast.error('No image selected', 'Please select an image first');
    if (image.size > 5 * 1024 * 1024) return toast.error('File too large', 'Max size is 5 MB');
    const formData = new FormData();
    formData.append('profile_picture', image);
    updateProfileImage(formData, {
      onSuccess: () => {
        toast.success('Success', 'Profile photo updated');
        router.refresh();
        setImage(undefined);
        setOpen(false);
      },
      onError: (error) => {
        logger.error(error);
        toast.error('Something went wrong', error.message?.toString());
      },
    });
  }

  return (
    <Dialog
      open={open}
      setOpen={(value) => { if (!value) setImage(undefined); setOpen(value); }}
      trigger={trigger}
      title="Change profile photo"
      description="Recommended size: 400×400 px · JPG or PNG · Max 5 MB"
      footer={
        <div className="flex w-full gap-3">
          <Button variant="outline" className="flex-1" onClick={() => { setImage(undefined); setOpen(false); }}>
            Cancel
          </Button>
          <Button className="flex-1" disabled={!image || isPending} loading={isPending} onClick={handleSave}>
            Save
          </Button>
        </div>
      }
    >
      <div className="my-4 flex flex-col items-center gap-4">
        {image ? (
          <Image
            src={URL.createObjectURL(image)}
            alt="preview"
            width={200}
            height={200}
            className="h-48 w-48 rounded-full object-cover ring-2 ring-border"
          />
        ) : (
          <div className="flex h-48 w-48 items-center justify-center rounded-full bg-accent">
            <ImagePlus className="h-10 w-10 text-muted-foreground" />
          </div>
        )}

        <label htmlFor="upload_profile_photo" className="cursor-pointer">
          <div className="flex items-center gap-2 rounded-lg border border-border px-4 py-2 text-sm font-medium text-foreground transition-colors hover:bg-accent">
            <ImagePlus className="h-4 w-4" />
            {image ? 'Change photo' : 'Upload photo'}
          </div>
          <input
            id="upload_profile_photo"
            type="file"
            accept="image/jpeg,image/png,image/gif"
            className="hidden"
            onChange={(e) => setImage(e.target.files?.[0])}
          />
        </label>
      </div>
    </Dialog>
  );
}
