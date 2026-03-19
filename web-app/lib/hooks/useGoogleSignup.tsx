'use client';

import { useMutation } from '@tanstack/react-query';

import { postClientDataAction } from 'lib/utils/clientDataActions';

interface GoogleSignupParams {
  id_token: string;
}

async function googleSignup({ id_token }: GoogleSignupParams) {
  return await postClientDataAction<ResponseType, { id_token: string }>('/auth/google', {
    id_token,
  });
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
