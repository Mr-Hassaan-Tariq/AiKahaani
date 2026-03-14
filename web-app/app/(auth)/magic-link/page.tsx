'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Check, XCircle, Loader2 } from 'lucide-react';
import Cookies from 'js-cookie';

import { authService } from 'lib/api';

// ── Page ─────────────────────────────────────────────────────────────
export default function MagicLinkPage() {
  const searchParams  = useSearchParams();
  const router        = useRouter();
  const email         = searchParams.get('email');
  const token         = searchParams.get('token');

  const [isResending, setIsResending]   = useState(false);
  const [resendMsg, setResendMsg]       = useState<string | null>(null);
  const [isVerifying, setIsVerifying]   = useState(!!token);
  const [verifyStatus, setVerifyStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [verifyMsg, setVerifyMsg]       = useState('');

  // ── Token verification ────────────────────────────────────────────
  useEffect(() => {
    if (!token) return;

    const verify = async () => {
      try {
        const partnerIdFromCookie = Cookies.get('partner_id');
        const response = await authService.verifyMagicLink(token, partnerIdFromCookie);

        if (response.user && response.access && response.refresh) {
          if (partnerIdFromCookie) Cookies.remove('partner_id');
          Cookies.set('access_token', response.access, { expires: 7 });
          localStorage.setItem('refresh_token', response.refresh);
          setVerifyStatus('success');
          setVerifyMsg('Verified successfully! Redirecting…');
          setTimeout(() => router.push('/'), 1800);
        } else {
          setVerifyStatus('error');
          setVerifyMsg('Invalid or expired magic link.');
        }
      } catch {
        setVerifyStatus('error');
        setVerifyMsg('Failed to verify the magic link. Please try again.');
      } finally {
        setIsVerifying(false);
      }
    };

    verify();
  }, [token, router]);

  // ── Resend ────────────────────────────────────────────────────────
  const handleResend = async () => {
    if (!email) {
      setResendMsg('No email found. Please go back and enter your email.');
      return;
    }
    setIsResending(true);
    setResendMsg(null);
    try {
      const response = await authService.sendMagicLink(email);
      setResendMsg(response.message || 'Magic link resent!');
    } catch {
      setResendMsg('Failed to resend. Please try again.');
    } finally {
      setIsResending(false);
    }
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-background px-4">

      {/* ── Decorative background orbs ── */}
      <div
        aria-hidden
        className="pointer-events-none absolute -left-48 -top-48 h-[600px] w-[600px] rounded-full bg-green-500/5 blur-[120px]"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute -bottom-24 -right-24 h-[400px] w-[400px] rounded-full bg-green-500/5 blur-[120px]"
      />

      {/* ── Card ── */}
      <div className="relative z-10 w-full max-w-[440px] rounded-2xl border border-border bg-card px-10 py-14 text-center shadow-sm">

        {/* ── Token verification state ── */}
        {token ? (
          <>
            <h1 className="text-2xl font-semibold text-foreground">
              {isVerifying ? 'Verifying your link…' : 'Magic Link Verification'}
            </h1>

            <div className="mt-8 flex flex-col items-center gap-4">
              {isVerifying ? (
                <Loader2 className="h-14 w-14 animate-spin text-primary" />
              ) : verifyStatus === 'success' ? (
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-success/10">
                  <Check className="h-8 w-8 text-success" strokeWidth={2.5} />
                </div>
              ) : (
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-destructive/10">
                  <XCircle className="h-8 w-8 text-destructive" />
                </div>
              )}

              {verifyMsg && (
                <p className={`text-sm font-medium ${
                  verifyStatus === 'error' ? 'text-destructive' : 'text-success'
                }`}>
                  {verifyMsg}
                </p>
              )}
            </div>

            {verifyStatus === 'error' && (
              <button
                onClick={() => router.push('/signup')}
                className="mt-8 text-sm font-medium text-primary hover:underline"
              >
                ← Back to sign in
              </button>
            )}
          </>

        ) : (
          /* ── Magic link sent state ── */
          <>
            <h1 className="text-2xl font-semibold text-foreground">Magic link sent!</h1>
            <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
              Check your inbox — click the link to
              <br />enter your workspace.
            </p>

            {/* Check icon */}
            <div className="mx-auto mt-8 flex h-16 w-16 items-center justify-center rounded-full bg-success/10">
              <Check className="h-8 w-8 text-success" strokeWidth={2.5} />
            </div>

            {/* Resend */}
            <p className="mt-8 text-sm text-muted-foreground">
              Didn&apos;t get the email?{' '}
              <button
                type="button"
                disabled={isResending}
                onClick={handleResend}
                className="font-medium text-primary hover:underline disabled:opacity-50"
              >
                {isResending ? 'Resending…' : 'Resend'}
              </button>
            </p>

            {resendMsg && (
              <p className="mt-2 text-xs text-muted-foreground">{resendMsg}</p>
            )}
          </>
        )}
      </div>
    </div>
  );
}
