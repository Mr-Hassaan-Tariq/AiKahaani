import { getUserProfile } from '@/(dashboard)/actions';

import ProfileCardDetail from './_components/ProfileCardDetail';
import ProfilePhotoCard from './_components/ProfilePhotoCard';
import Col from 'components/ui/Col';
import Text from 'components/ui/Text';

export default async function Page() {
  const { data, error, isError } = await getUserProfile();

  return (
    <Col className="gap-10 text-white">
      {isError && (
        <Text variant="base" className="text-brand-secondary">
          {error.message?.toString()}
        </Text>
      )}
      <ProfilePhotoCard profileImage={data?.profile_picture} fullname={data?.fullname} />
      <ProfileCardDetail profile={data} />
    </Col>
  );
}
