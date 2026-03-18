'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Wand2 } from 'lucide-react';
import * as yup from 'yup';

import GoogleAuthComponent from './_components/GoogleAuthComponent';
import { authService } from 'lib/api';
import { Button } from 'components/ui/Button';
import { Input } from 'components/ui/Input';

// ── Validation ───────────────────────────────────────────────────────
const signupSchema = yup.object({
  email: yup
    .string()
    .required('Email is required')
    .email('Please enter a valid email address')
    .trim(),
});
// ── Page ─────────────────────────────────────────────────────────────
export default function Signup() {
  const router = useRouter();

  const [email, setEmail] = useState('');
  const [emailError, setEmailError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // ── Submit ────────────────────────────────────────────────────────
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setEmailError('');
    setIsLoading(true);

    try {
      await signupSchema.validate({ email }, { abortEarly: false });
      const response = await authService.sendMagicLink(email);

      if (response.message === 'Magic link sent to your email') {
        router.push(`/magic-link?email=${encodeURIComponent(email)}`);
      }
    } catch (err) {
      if (err instanceof yup.ValidationError) {
        setEmailError(err.inner[0]?.message ?? err.message);
      } else {
        setEmailError('Failed to send magic link. Please try again.');
      }
    } finally {
      setIsLoading(false);
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

      {/* ── Auth card ── */}
      <div className="relative z-10 w-full max-w-[480px] rounded-2xl border border-border bg-card px-10 py-14 shadow-sm">
        {/* Heading */}
        <h1 className="text-center text-3xl font-semibold tracking-tight text-foreground">
          Let&apos;s get you creating
        </h1>
        <p className="mt-3 text-center text-sm leading-relaxed text-muted-foreground">
          Sign in or create an account in seconds
          <br />— no password needed.
        </p>

        {/* Form */}
        <form onSubmit={handleSubmit} className="mt-8 flex flex-col gap-5">
          <Input
            label="Email"
            type="email"
            placeholder="example@email.com"
            value={email}
            error={emailError}
            onChange={(e) => {
              setEmail(e.target.value);
              if (emailError) setEmailError('');
            }}
          />

          <Button type="submit" loading={isLoading} size="lg" className="w-full">
            <Wand2 className="h-4 w-4" />
            Send me the magic link
          </Button>
        </form>

        {/* Divider */}
        <div className="my-6 flex items-center gap-3">
          <div className="h-px flex-1 bg-border" />
          <span className="text-xs text-muted-foreground">or</span>
          <div className="h-px flex-1 bg-border" />
        </div>

        {/* Google */}
        <GoogleAuthComponent />
      </div>
    </div>
  );
}
