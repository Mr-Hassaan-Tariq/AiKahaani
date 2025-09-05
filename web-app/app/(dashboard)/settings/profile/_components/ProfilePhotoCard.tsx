'use client';

import ChangePhotoModal from './ChangePhotoModal';
import { basketIcon, changePhotoIcon } from './components';
import DeletePhotoModal from './DeletePhotoModal';
import Button from 'components/ui/Button';
import Card from 'components/ui/Card';
import ClientImage from 'components/ui/ClientImage';
import Col from 'components/ui/Col';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';

export default function ProfilePhotoCard({ profileImage }: { profileImage?: string }) {
  return (
    <Card>
      <Col className="gap-6 lg:gap-8">
        <Text variant="2xl" className="text-xl text-white lg:text-2xl">
          Profile Photo
        </Text>

        <Row className="flex-col justify-normal gap-6 md:flex-row">
          {/* <Image
            src={profileImage || brokenImage}
            alt="DP"
            width={500}
            height={500}
            priority={true}
            className="h-[120px] w-[120px] rounded-full bg-white/10 object-cover"
            onError={(e) => {
              e.currentTarget.src = brokenImage.src;
            }}
          /> */}

          <ClientImage
            src={profileImage || ''}
            alt="DP"
            width={500}
            height={500}
            priority={true}
            className="h-[120px] w-[120px] rounded-full bg-white/10 object-cover"
          />

          <Col className="gap-6">
            <Col className="gap-3">
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
            <Row className="justify-center lg:justify-normal">
              <ChangePhotoModal
                trigger={
                  <Button variant="gray" className="flex w-fit items-center ...">
                    {changePhotoIcon} Change photo
                  </Button>
                }
              />

              <DeletePhotoModal
                trigger={
                  <Button
                    variant="red"
                    className="flex w-fit items-center justify-center bg-[#FF50500D]"
                  >
                    {basketIcon} Remove photo
                  </Button>
                }
              />
            </Row>
          </Col>
        </Row>
      </Col>
    </Card>
  );
}
