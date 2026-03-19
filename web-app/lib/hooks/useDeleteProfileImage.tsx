'use client';

import { useMutation } from '@tanstack/react-query';

import { patchClientDataAction } from 'lib/utils/clientDataActions';

async function deleteProfileImage() {
  // Clear profile picture by patching profile with null URL
  return await patchClientDataAction('/v1/users/me', { profile_picture_url: null });
}

export default function useDeleteProfileImage() {
  return useMutation({ mutationFn: deleteProfileImage });
}
