'use client';

import { useMutation } from '@tanstack/react-query';

import { postClientDataAction } from 'lib/utils/clientDataActions';

interface GoogleSignupParams {
  id_token: string;
  partnerId?: string;
}

async function googleSignup({ id_token, partnerId }: GoogleSignupParams) {
  const payload: { id_token: string; partner_id?: string } = { id_token };

  if (partnerId) {
    payload.partner_id = partnerId;
  }

  return await postClientDataAction<ResponseType, typeof payload>('auth/google/', payload);
}

export default function useGoogleSignup() {
  return useMutation({ mutationFn: googleSignup });
}

interface ResponseType {
  access: string;
  refresh: string;
  // user: {
  //   id: string;
  //   email: string;
  //   fullname: string;
  //   username: string;
  // };
}
