import { getUserProfile } from '@/(dashboard)/actions';

import ProfileCardDetail from './_components/ProfileCardDetail';
import ProfilePhotoCard from './_components/ProfilePhotoCard';
import { Button } from 'components/ui/Button';

export default async function Page() {
  const { data, error, isError } = await getUserProfile();

  return (
    <div className="flex flex-col gap-6">
      {isError && (
        <p className="text-sm text-destructive">{error?.message?.toString()}</p>
      )}

      <ProfilePhotoCard profileImage={data?.profile_picture} fullName={data?.username} />
      <ProfileCardDetail profile={data} />

      {/* Footer actions */}
      <div className="flex items-center justify-end gap-3 pt-2 pb-4">
        <Button variant="outline">Discard Changes</Button>
        <Button variant="primary" disabled>Save Profile</Button>
      </div>
    </div>
  );
}
