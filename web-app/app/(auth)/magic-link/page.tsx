'use client';

import { useEffect, useState } from 'react';
import Image from 'next/image';
import { useRouter, useSearchParams } from 'next/navigation';
import { CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/solid';
import Cookies from 'js-cookie';

import { authService } from 'lib/api';

export default function MagicLinkSent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const email = searchParams.get('email');
  const token = searchParams.get('token');

  const [isResending, setIsResending] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [isVerifying, setIsVerifying] = useState<boolean>(!!token);
  const [isError, setIsError] = useState<boolean>(false);

  // Verification logic
  useEffect(() => {
    if (token) {
      const verifyMagicLink = async () => {
        setMessage('Verifying your link...');
        setIsError(false);

        try {
          const response = await authService.verifyMagicLink(token);
          if (response.user && response.access) {
            Cookies.set('access_token', response.access, { expires: 7 });
            setMessage('Verified successfully! Redirecting...');
            setIsError(false);
            setTimeout(() => {
              router.push('/');
            }, 2000);
          } else {
            setMessage('Invalid or expired magic link.');
            setIsError(true);
          }
        } catch {
          setMessage('Failed to verify the magic link.');
          setIsError(true);
        } finally {
          setIsVerifying(false);
        }
      };
      verifyMagicLink();
    }
  }, [token, router]);

  const handleResend = async () => {
    if (!email) {
      setMessage('No email found. Please go back and enter your email again.');
      return;
    }

    setIsResending(true);
    setMessage(null);

    try {
      const response = await authService.sendMagicLink(email);
      setMessage(response.message || 'Magic link resent!');
    } catch {
      setMessage('Failed to resend magic link. Please try again.');
    } finally {
      setIsResending(false);
    }
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#0a0a0a] px-3">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,#1a2e1d,transparent_40%)] opacity-50" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom_right,#1a2e1d,transparent_40%)] opacity-50" />

      {/* Card */}
      <div className="relative z-10 w-full max-w-md rounded-2xl border border-[#BAFF381F] bg-[#161616] p-10 text-center shadow-lg">
        {token ? (
          <>
            <h1 className="text-4xl font-bold text-white">
              {isVerifying ? 'Verifying...' : 'Magic Link Verification'}
            </h1>
            {message && (
              <div className="mt-4 flex flex-col items-center justify-center space-y-3">
                {/* Icon */}
                <div>
                  {isVerifying ? null : isError ? (
                    <XCircleIcon className="h-20 w-20 text-red-500" />
                  ) : (
                    <CheckCircleIcon className="h-20 w-20 text-green-400" />
                  )}
                </div>

                {/* Message */}
                <p className={`mt-2 text-sm ${isError ? 'text-red-500' : 'text-green-400'}`}>
                  {message}
                </p>
              </div>
            )}
          </>
        ) : (
          <>
            <h1 className="text-4xl font-bold text-white">Magic link sent!</h1>
            <p className="text-md mt-4 text-gray-400">
              Check your inbox — click the link to <br /> enter your workspace.
            </p>
            <div className="mt-8 flex items-center justify-center">
              <Image src="/images/right-check.svg" alt="check" width={100} height={100} />
            </div>
            <p className="mt-6 text-sm text-gray-500">
              Didn’t get the email?{' '}
              <button
                type="button"
                disabled={isResending}
                className="ml-2 text-white hover:underline"
                onClick={handleResend}
              >
                {isResending ? 'Resending...' : 'Resend'}
              </button>
            </p>
            {message && <p className="mt-3 text-sm text-green-400">{message}</p>}
          </>
        )}
      </div>
    </div>
  );
}
