'use client';

import { useMutation } from '@tanstack/react-query';

import { postClientDataAction } from 'lib/utils/clientDataActions';

async function googleSignup(token: string) {
  return await postClientDataAction<ResponseType, { id_token: string }>('auth/google/', {
    id_token: token,
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
