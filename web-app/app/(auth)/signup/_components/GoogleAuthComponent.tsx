'use client';

import { useGoogleLogin } from '@react-oauth/google';
import Cookies from 'js-cookie';
import { FcGoogle } from 'react-icons/fc';

import useGoogleSignup from 'lib/hooks/useGoogleSignup';
import useToast from 'lib/utils/useToast';
import PageLoader from 'components/ui/PageLoader';

export default function GoogleAuthComponent() {
  const toast = useToast();
  const { mutate: googleSignup, isPending } = useGoogleSignup();

  const onSubmit = async (token: string) => {
    console.log('token is ', token);
    googleSignup(token, {
      onSuccess: (response) => {
        toast.success('Success', 'Successfully logged in');
        Cookies.set('access_token', response.access);
        window.location.href = '/';
      },
      onError: (err) => {
        toast.error('Error signing up with Google', err.message);
      },
    });
  };

  const handleGoogleLogin = useGoogleLogin({
    flow: 'implicit',
    onSuccess: async (response) => {
      const { access_token } = response;
      await onSubmit(access_token);
    },
    onError: () => {},
  });

  return (
    <p
      role="button"
      onClick={() => handleGoogleLogin()}
      className="flex w-full cursor-pointer items-center justify-center space-x-2 rounded-full border border-gray-700 bg-[#1a1a1a] py-3 font-medium text-white transition hover:bg-[#222222]"
    >
      {isPending ? (
        <PageLoader size="2xl" color="white" />
      ) : (
        <>
          <FcGoogle className="text-xl" />
          <span className="font-bold">Continue with Google</span>
        </>
      )}
    </p>
    // <Link
    //   href={`https://accounts.google.com/o/oauth2/v2/auth?client_id=${env.NEXT_PUBLIC_GOOGLE_CLIENT_ID}&redirect_uri=${domain}/&response_type=code&scope=openid%20email%20profile&access_type=offline&state=xyz123`}
    //   className="flex w-full items-center justify-center space-x-2 rounded-full border border-gray-700 bg-[#1a1a1a] py-3 font-medium text-white transition hover:bg-[#222222]"
    // >
    //   {isPending ? (
    //     <PageLoader size="2xl" color="white" />
    //   ) : (
    //     <>
    //       <FcGoogle className="text-xl" />
    //       <span className="font-bold">Continue with Google</span>
    //     </>
    //   )}
    // </Link>
  );
}
