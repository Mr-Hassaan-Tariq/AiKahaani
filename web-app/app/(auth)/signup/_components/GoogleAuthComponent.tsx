'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { env } from 'env.mjs';
import Cookies from 'js-cookie';
import { FcGoogle } from 'react-icons/fc';

import { SetAccessToken } from '../actions';
import useGoogleSignup from 'lib/hooks/useGoogleSignup';
import useToast from 'lib/utils/useToast';
import PageLoader from 'components/ui/PageLoader';

export default function GoogleAuthComponent() {
  const toast = useToast();
  const searchParams = useSearchParams();
  // const domain = typeof window !== 'undefined' ? window.location.origin : '';
  // const domain = 'https://web-app-production-495a.up.railway.app';
  // const domain = 'http://localhost:3000';
  const { mutate: googleSignup, isPending } = useGoogleSignup();

  useEffect(() => {
    if (!isPending) {
      const token = searchParams.get('code');
      if (token) {
        googleSignup(token, {
          onSuccess: async (response) => {
            toast.success('Success', 'Successfully logged in');
            Cookies.set('access_token', response.access);
            Cookies.set('refresh_token', response.refresh);
            localStorage.setItem('refresh_token', response.refresh);
            SetAccessToken(response.access);
            window.location.href = '/';
          },
          onError: (err) => {
            toast.error('Error signing up with Google', err.message);
          },
        });
      }
    }

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <Link
      href={`https://accounts.google.com/o/oauth2/v2/auth?client_id=${env.NEXT_PUBLIC_GOOGLE_CLIENT_ID}&redirect_uri=https://web-app-production-495a.up.railway.app/&response_type=code&scope=openid%20email%20profile&access_type=offline&state=xyz123`}
      className="flex w-full items-center justify-center space-x-2 rounded-full border border-gray-700 bg-[#1a1a1a] py-3 font-medium text-white transition hover:bg-[#222222]"
    >
      {isPending ? (
        <PageLoader size="2xl" color="white" />
      ) : (
        <>
          <FcGoogle className="text-xl" />
          <span className="font-bold">Continue with Google</span>
        </>
      )}
    </Link>
  );
}
