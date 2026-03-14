import { getUserProfile } from '@/(dashboard)/actions';

import ProfileCardDetail from './_components/ProfileCardDetail';
import ProfilePhotoCard from './_components/ProfilePhotoCard';

export default async function Page() {
  const { data, error, isError } = await getUserProfile();

  return (
    <div className="flex flex-col gap-6 max-w-2xl">
      {isError && (
        <p className="text-sm text-destructive">{error?.message?.toString()}</p>
      )}
      <ProfilePhotoCard profileImage={data?.profile_picture} fullName={data?.username} />
      <ProfileCardDetail profile={data} />
    </div>
  );
}
