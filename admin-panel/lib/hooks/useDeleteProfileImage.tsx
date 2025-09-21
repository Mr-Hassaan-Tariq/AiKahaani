'use client';

import { useMutation } from '@tanstack/react-query';

import { deleteClientDataAction } from 'lib/utils/clientDataActions';

async function deleteProfileImage() {
  return await deleteClientDataAction('v1/users/profile-picture');
}

export default function useDeleteProfileImage() {
  return useMutation({ mutationFn: deleteProfileImage });
}
