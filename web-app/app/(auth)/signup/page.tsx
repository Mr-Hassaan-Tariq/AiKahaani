'use client';

import { useEffect, useState } from 'react';
import Image from 'next/image';
import { useRouter, useSearchParams } from 'next/navigation';
import GoogleAuthComponent from '@/(auth)/signup/_components/GoogleAuthComponent';
import Cookies from 'js-cookie';
import * as yup from 'yup';

import MaginpanIcon from '/public/images/maginpan.svg';
import { authService } from 'lib/api';
import useToast from 'lib/utils/useToast';
import Button from 'components/common/Button';
import TextField from 'components/common/TextField';

// Yup validation schema
const signupSchema = yup.object({
  email: yup
    .string()
    .required('Email is required')
    .email('Please enter a valid email address')
    .trim(),
});

type SignupFormData = yup.InferType<typeof signupSchema>;

export default function Signup() {
  const toast = useToast();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [formData, setFormData] = useState<SignupFormData>({
    email: '',
  });
  const [errors, setErrors] = useState<Partial<SignupFormData>>({});
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const [partnerId, setPartnerId] = useState<string | null>(null);
  useEffect(() => {
    // Check for ref link in URL
    const refCode = searchParams.get('ref') || searchParams.get('via');

    if (refCode && typeof window !== 'undefined') {
      // Determine device type
      const deviceType = /Mobile|Android|iPhone|iPad/.test(navigator.userAgent)
        ? 'mobile'
        : 'desktop';

      // Get current page URL
      const pageUrl = window.location.href;

      // Call getToltPartnerid function
      authService
        .getToltPartnerid({
          param_name: searchParams.get('via') ? 'via' : 'ref',
          referral_code: refCode,
          page_url: pageUrl,
          device_type: deviceType,
        })
        .then((response: any) => {
          const partnerIdValue = response.partner_id;
          setPartnerId(partnerIdValue);
          // Save partner ID to cookies
          if (partnerIdValue) {
            Cookies.set('partner_id', partnerIdValue, { expires: 30 }); // Expires in 30 days
          }
        })
        .catch((error) => {
          console.error(error);
          toast.error('Link not working.');
        });
    }
  }, [searchParams, toast]);
  // Handle input change
  const handleInputChange = (field: keyof SignupFormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error when user types
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }));
    }
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Reset errors
    setErrors({});
    setIsLoading(true);

    try {
      // Validate form data
      await signupSchema.validate(formData, { abortEarly: false });

      const response = await authService.sendMagicLink(formData.email);

      if (response.message === 'Magic link sent to your email') {
        router.push(`/magic-link?email=${encodeURIComponent(formData.email)}`);
      }
    } catch (validationError) {
      if (validationError instanceof yup.ValidationError) {
        // Convert Yup errors to our format
        const yupErrors: Partial<SignupFormData> = {};
        validationError.inner.forEach((error) => {
          if (error.path) {
            yupErrors[error.path as keyof SignupFormData] = error.message;
          }
        });
        setErrors(yupErrors);
      } else {
        // Handle other errors
        setErrors({ email: 'Failed to send magic link. Please try again.' });
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#0a0a0a] px-3">
      {/* Background grid effect */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,#1a2e1d,transparent_40%)] opacity-100" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom_right,#1a2e1d,transparent_40%)] opacity-100" />

      {/* Card */}
      <div className="relative z-10 w-full max-w-xl rounded-2xl border border-[#BAFF381F] bg-[#161616] p-8 shadow-lg">
        {/* Heading */}
        <h1 className="text-center text-4xl font-bold text-white">Let&apos;s get you creating</h1>
        <p className="mt-2 text-center text-lg text-gray-400">
          Sign in or create an account in seconds <br></br> — no password needed.
        </p>

        <form onSubmit={handleSubmit} className="mt-6">
          {/* Email input */}
          <div className="mt-6">
            <TextField
              label="Email"
              placeholder="Enter your email"
              type="email"
              className={`w-full rounded-xl border ${
                errors.email ? 'border-red-500' : 'border-transparent'
              } bg-[#2d2d2d] px-4 py-3 text-white placeholder-[#aaaca6] outline-none focus:border-green-500`}
              value={formData.email}
              onChange={(value) => handleInputChange('email', value)}
            />
            {errors.email && <p className="mt-1 text-sm text-red-500">{errors.email}</p>}
          </div>

          <Button type="submit" disabled={isLoading} className="mt-10">
            {isLoading ? (
              <>
                <div className="h-5 w-5 animate-spin rounded-full border-2 border-black border-t-transparent"></div>
                <span>Sending...</span>
              </>
            ) : (
              <>
                <Image src={MaginpanIcon} alt="maginpan" width={20} height={20} />
                <span className="font-bold"> Send me the magic link</span>
              </>
            )}
          </Button>
        </form>

        {/* Divider */}
        <div className="my-6 flex items-center">
          <div className="h-px flex-grow bg-gray-700"></div>
          <span className="px-2 text-sm text-gray-500">or</span>
          <div className="h-px flex-grow bg-gray-700"></div>
        </div>

        {/* Google button */}
        <GoogleAuthComponent partnerId={partnerId ?? undefined} />
      </div>
    </div>
  );
}
