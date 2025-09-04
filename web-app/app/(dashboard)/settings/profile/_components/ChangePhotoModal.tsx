'use client';

import { ReactNode, useState } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { ImagePlus } from 'lucide-react';

import { imageUploadIcon } from './components';
import useUpdateProfileImage from 'lib/hooks/useUpdateProfileImage';
import { logger } from 'lib/logger';
import useToast from 'lib/utils/useToast';
import Button from 'components/ui/Button';
import Col from 'components/ui/Col';
import Dialog from 'components/ui/Dialog';
import PageLoader from 'components/ui/PageLoader';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';

export default function ChangePhotoModal({ trigger }: { trigger: ReactNode }) {
  const toast = useToast();
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [image, setImage] = useState<File | undefined>();
  const { isPending, mutate: updateProfileImage } = useUpdateProfileImage();

  function handleSave() {
    if (!image) return toast.error('Something went wrong', 'Please select an image');
    if (image.size > 5 * 1024 * 1024)
      return toast.error('File too large', 'Please select an image smaller than 5MB');

    const formData = new FormData();
    formData.append('profile_picture', image);
    updateProfileImage(formData, {
      onSuccess: async () => {
        toast.success('Success', 'Profile image updated successfully');
        router.refresh();
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
      setOpen={(value) => {
        setOpen(value);
        if (!value) {
          setImage(undefined);
        }
      }}
      trigger={trigger}
      title="Change your profile photo"
      description={
        <Col className="mt-5 items-center justify-center gap-2">
          <Row className="justify-normal">
            <Text variant="base">Recommended size:</Text>{' '}
            <Text variant="base" className="font-semibold">
              400×400 px
            </Text>
          </Row>
          <Row className="justify-normal">
            <Text variant="base">Accepted formats:</Text>{' '}
            <Text variant="base" className="font-semibold">
              JPG, PNG · Max file size: 5MB
            </Text>
          </Row>
        </Col>
      }
      footer={
        <Row className="w-full gap-6">
          <Button
            variant="gray"
            onClick={() => {
              setOpen(false);
              setImage(undefined);
            }}
          >
            <Text
              variant="base"
              className="font-extrabold [font-feature-settings:'liga'_off,'clig'_off]"
            >
              Cancel
            </Text>
          </Button>
          <Button type="button" disabled={!image || isPending} onClick={handleSave}>
            {isPending ? 'Saving...' : 'Save'}
          </Button>
        </Row>
      }
    >
      {isPending && <PageLoader size="2xl" />}
      <Col className="my-5 items-center gap-8">
        {image ? (
          <Image
            src={URL.createObjectURL(image)}
            alt="profile"
            width={250}
            height={250}
            className="size-[250px] rounded"
          />
        ) : (
          imageUploadIcon
        )}

        <div>
          <input
            className="hidden"
            id="upload_docs"
            accept="image/jpeg, image/png, image/gif"
            type="file"
            onChange={(e) => {
              if (e.target.files) {
                setImage(e.target.files[0]);
              } else {
                setImage(undefined);
              }
            }}
          />
          <label htmlFor="upload_docs">
            <div className="flex h-[52px] w-full items-center justify-center gap-2 rounded-full bg-white/10 px-5 backdrop-blur-[2px] hover:bg-white/10 hover:opacity-70">
              <ImagePlus size={16} />
              <Text
                variant="base"
                className="flex font-extrabold [font-feature-settings:'liga'_off,'clig'_off]"
              >
                Upload new photo
              </Text>
            </div>
          </label>
        </div>
      </Col>
    </Dialog>
  );
}
