'use client';

import { useMutation } from '@tanstack/react-query';
import Cookies from 'js-cookie';

import { baseUrl, method } from 'lib/api';
import { processError } from 'lib/utils/clientDataActions';

async function updateProfileImage(formData: FormData) {
  const token = Cookies.get('access_token');

  if (!token) return (window.location.href = '/signup');

  const res = await fetch(`${baseUrl.replace(/\/$/, '')}/v1/users/me`, {
    method: method.patch,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      profile_picture_url: formData.get('profile_picture_url') ?? formData.get('profile_picture'),
    }),
  });
  if (!res.ok) throw await processError(res);
  return res.json();
}

export default function useUpdateProfileImage() {
  return useMutation({ mutationFn: updateProfileImage });
}
