import ProfileCardDetail from './_components/ProfileCardDetail';
import ProfilePhotoCard from './_components/ProfilePhotoCard';
import Col from 'components/ui/Col';

export default function Page() {
  return (
    <Col className="gap-10 text-white">
      <ProfilePhotoCard />
      <ProfileCardDetail />
    </Col>
  );
}
