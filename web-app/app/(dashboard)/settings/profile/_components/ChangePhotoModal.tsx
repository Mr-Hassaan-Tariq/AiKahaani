'use client';

import { useState } from 'react';
import Image from 'next/image';
import { ImagePlus } from 'lucide-react';

import Col from 'components/ui/Col';
import Dialog from 'components/ui/Dialog';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';
import { Button } from 'components/shadcn_ui/button';

export default function ChangePhotoModal({ trigger }: { trigger: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  const [image, setImage] = useState<File | undefined>();
  return (
    <Dialog
      open={open}
      setOpen={setOpen}
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
            className="h-[52px] w-full rounded-full bg-white/10 backdrop-blur-[2px] hover:bg-white/10 hover:opacity-70"
            onClick={() => setOpen(false)}
          >
            <Text
              variant="base"
              className="font-extrabold [font-feature-settings:'liga'_off,'clig'_off]"
            >
              Cancel
            </Text>
          </Button>
          <Button
            type="submit"
            disabled={!image}
            className="h-[52px] w-full rounded-full bg-gradient-to-r from-[#2BFF13] to-[#20BF0E] hover:opacity-70 disabled:opacity-50"
          >
            <Text
              variant="base"
              className="font-extrabold text-[#0E0F0C] [font-feature-settings:'liga'_off,'clig'_off]"
            >
              Save
            </Text>
          </Button>
        </Row>
      }
    >
      <Col className="my-5 items-center gap-8">
        {image ? (
          <Image
            src={URL.createObjectURL(image)}
            alt="profile"
            width={380}
            height={380}
            className="size-[380px] rounded"
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

const imageUploadIcon = (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="120"
    height="120"
    viewBox="0 0 120 120"
    fill="none"
  >
    <path
      opacity="0.4"
      fill-rule="evenodd"
      clip-rule="evenodd"
      d="M102.82 15.9202C105 20.1984 105 25.799 105 37V61.161C100.512 58.8222 95.4106 57.5 90 57.5C77.1536 57.5 66.048 64.9535 60.7718 75.7718L39.5711 54.5711C35.6658 50.6658 29.3342 50.6658 25.4289 54.5711L5.00051 74.9995L5 37C5 25.799 5 20.1984 7.17987 15.9202C9.09734 12.1569 12.1569 9.09734 15.9202 7.17987C20.1984 5 25.799 5 37 5H73C84.201 5 89.8016 5 94.0798 7.17987C97.8431 9.09734 100.903 12.1569 102.82 15.9202ZM62.5 37.5C62.5 43.0228 66.9772 47.5 72.5 47.5C78.0229 47.5 82.5 43.0228 82.5 37.5C82.5 31.9772 78.0229 27.5 72.5 27.5C66.9772 27.5 62.5 31.9772 62.5 37.5Z"
      fill="#00B559"
    />
    <path
      d="M73.1131 2.5H36.8869C31.3821 2.49999 27.0974 2.49998 23.6605 2.78079C20.1708 3.0659 17.3355 3.65292 14.7852 4.95235C10.5516 7.10951 7.10951 10.5516 4.95235 14.7852C3.65292 17.3355 3.0659 20.1708 2.78079 23.6605C2.5 27.0971 2.5 31.3814 2.5 36.8856V74.95L2.50012 74.975L2.5 74.9995V75.0939C2.5 79.6732 2.5 83.2392 2.6961 86.1133C2.89509 89.0297 3.3043 91.4173 4.21271 93.6104C6.49632 99.1235 10.8765 103.504 16.3896 105.787C18.5827 106.696 20.9703 107.105 23.8867 107.304C26.7609 107.5 30.3257 107.5 34.9052 107.5H62.6091C61.5983 105.921 60.7203 104.249 59.9908 102.5H35C30.3064 102.5 26.9114 102.499 24.2271 102.316C21.5652 102.134 19.7854 101.782 18.303 101.168C14.015 99.3917 10.6083 95.985 8.83211 91.697C8.21812 90.2146 7.86612 88.4348 7.6845 85.7729C7.51511 83.2902 7.50122 80.1994 7.5001 76.0354L27.1967 56.3388C30.1256 53.4099 34.8744 53.4099 37.8033 56.3389L59.6961 78.2318C60.3397 76.5757 61.1151 74.9855 62.0094 73.474L41.3388 52.8033C36.4573 47.9218 28.5427 47.9218 23.6612 52.8033L7.5 68.9645V37C7.5 31.3582 7.50195 27.2772 7.76418 24.0676C8.02403 20.8872 8.52695 18.7831 9.40739 17.0552C11.0852 13.7623 13.7623 11.0852 17.0552 9.40739C18.7831 8.52695 20.8872 8.02403 24.0676 7.76418C27.2772 7.50195 31.3582 7.5 37 7.5H73C78.6418 7.5 82.7228 7.50195 85.9324 7.76418C89.1128 8.02403 91.2169 8.52695 92.9448 9.40739C96.2377 11.0852 98.9148 13.7623 100.593 17.0552C101.473 18.7831 101.976 20.8872 102.236 24.0676C102.498 27.2772 102.5 31.3582 102.5 37V59.9908C104.249 60.7203 105.921 61.5983 107.5 62.6091V36.8869C107.5 31.3823 107.5 27.0973 107.219 23.6605C106.934 20.1708 106.347 17.3355 105.048 14.7852C102.89 10.5516 99.4484 7.10951 95.2148 4.95235C92.6645 3.65292 89.8292 3.0659 86.3395 2.78079C82.9026 2.49998 78.6179 2.49999 73.1131 2.5Z"
      fill="#00B559"
    />
    <path
      fill-rule="evenodd"
      clip-rule="evenodd"
      d="M85 37.5C85 30.5964 79.4036 25 72.5 25C65.5964 25 60 30.5964 60 37.5C60 44.4036 65.5964 50 72.5 50C79.4036 50 85 44.4036 85 37.5ZM72.5 30C76.6421 30 80 33.3579 80 37.5C80 41.6421 76.6421 45 72.5 45C68.3579 45 65 41.6421 65 37.5C65 33.3579 68.3579 30 72.5 30Z"
      fill="#00B559"
    />
    <path
      d="M102.5 90C102.5 91.3807 101.381 92.5 100 92.5H92.5V100C92.5 101.381 91.3807 102.5 90 102.5C88.6193 102.5 87.5 101.381 87.5 100V92.5H80C78.6193 92.5 77.5 91.3807 77.5 90C77.5 88.6193 78.6193 87.5 80 87.5H87.5V80C87.5 78.6193 88.6193 77.5 90 77.5C91.3807 77.5 92.5 78.6193 92.5 80V87.5H100C101.381 87.5 102.5 88.6193 102.5 90Z"
      fill="#00B559"
    />
    <path
      fill-rule="evenodd"
      clip-rule="evenodd"
      d="M90 62.5C74.8122 62.5 62.5 74.8122 62.5 90C62.5 105.188 74.8122 117.5 90 117.5C105.188 117.5 117.5 105.188 117.5 90C117.5 74.8122 105.188 62.5 90 62.5ZM67.5 90C67.5 77.5736 77.5736 67.5 90 67.5C102.426 67.5 112.5 77.5736 112.5 90C112.5 102.426 102.426 112.5 90 112.5C77.5736 112.5 67.5 102.426 67.5 90Z"
      fill="#00B559"
    />
  </svg>
);
