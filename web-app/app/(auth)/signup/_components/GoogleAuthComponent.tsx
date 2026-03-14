'use client';

import { useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { env } from 'env.mjs';
import Cookies from 'js-cookie';
import { FcGoogle } from 'react-icons/fc';

import { SetAccessToken } from '../actions';
import useGoogleSignup from 'lib/hooks/useGoogleSignup';
import useToast from 'lib/utils/useToast';
import { Spinner } from 'components/ui/Spinner';

export default function GoogleAuthComponent() {
  const toast = useToast();
  const searchParams = useSearchParams();
  const { mutate: googleSignup, isPending } = useGoogleSignup();

  useEffect(() => {
    if (!isPending) {
      const token = searchParams.get('code');
      if (token) {
        googleSignup(
          { id_token: token },
          {
            onSuccess: async (response) => {
              toast.success('Success', 'Successfully logged in');
              Cookies.set('access_token', response.access);
              Cookies.set('refresh_token', response.refresh);
              localStorage.setItem('refresh_token', response.refresh);
              SetAccessToken(response.access);
              window.location.href = '/';
            },
            onError: (err) => {
              toast.error('Error signing in with Google', err.message);
            },
          },
        );
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const googleAuthUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${env.NEXT_PUBLIC_GOOGLE_CLIENT_ID}&redirect_uri=${env.NEXT_PUBLIC_WEBSITE_URL}/&response_type=code&scope=openid%20email%20profile&access_type=offline&state=xyz123`;

  return (
    <a
      href={googleAuthUrl}
      className="flex w-full items-center justify-center gap-3 rounded-lg border border-border bg-secondary py-3 text-sm font-medium text-foreground transition-colors hover:bg-muted"
    >
      {isPending ? (
        <Spinner size="sm" color="muted" />
      ) : (
        <>
          <FcGoogle className="h-5 w-5 shrink-0" />
          Continue with Google
        </>
      )}
    </a>
  );
}
