'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useGoogleLogin } from '@react-oauth/google';
import { FcGoogle } from 'react-icons/fc';

export default function GoogleAuthComponent() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const domain = typeof window !== 'undefined' ? window.location.origin : '';

  const handleGoogleLogin = useGoogleLogin({
    flow: 'auth-code',
    scope: 'openid email profile',
    hosted_domain: domain,
    onSuccess: async (response) => {
      console.log('response auth code', response);
      setLoading(true);
      try {
        const res = await fetch(
          'https://tubegenius-production-b4b6.up.railway.app/api/auth/google/',
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              id_token: response.code,
            }),
          },
        );
        const data = await res.json();
        console.log('success', data);
        alert(JSON.stringify(data));
        router.push('/');
      } catch (error) {
        console.log('error', error);
        alert(JSON.stringify(error));
      } finally {
        setLoading(false);
      }
    },
    onError: (err) => {
      console.log('Auth error:', err);
      alert(JSON.stringify(err));
    },
  });
  return (
    <button
      onClick={handleGoogleLogin}
      disabled={loading}
      className="flex w-full items-center justify-center space-x-2 rounded-full border border-gray-700 bg-[#1a1a1a] py-3 font-medium text-white transition hover:bg-[#222222]"
    >
      {loading ? (
        <div>Loading...</div>
      ) : (
        <>
          <FcGoogle className="text-xl" />
          <span>Continue with Google</span>
        </>
      )}
    </button>
  );
}
