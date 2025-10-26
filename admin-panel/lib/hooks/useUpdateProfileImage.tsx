'use client';

import { useMutation } from '@tanstack/react-query';
import Cookies from 'js-cookie';

import { baseUrl, method } from 'lib/api';
import { processError } from 'lib/utils/clientDataActions';

async function updateProfileImage(formData: FormData) {
  const token = Cookies.get('access_token');

  if (!token) return (window.location.href = '/signin');

  const res = await fetch(`${baseUrl}v1/users/profile-picture`, {
    method: method.patch,
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });
  if (!res.ok) throw await processError(res);
  return res.json();
}

export default function useUpdateProfileImage() {
  return useMutation({ mutationFn: updateProfileImage });
}
