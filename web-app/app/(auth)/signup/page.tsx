'use client';

import { useState } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import GoogleAuthComponent from '@/(auth)/signup/_components/GoogleAuthComponent';
import { GoogleOAuthProvider } from '@react-oauth/google';
import { env } from 'env.mjs';
import * as yup from 'yup';

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
  const router = useRouter();
  const [formData, setFormData] = useState<SignupFormData>({
    email: '',
  });
  const [errors, setErrors] = useState<Partial<SignupFormData>>({});
  const [isLoading, setIsLoading] = useState<boolean>(false);

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

    router.push('/magic-link');
    // Reset errors
    setErrors({});
    setIsLoading(true);

    try {
      // Validate form data
      await signupSchema.validate(formData, { abortEarly: false });

      // Simulate API call - replace with actual magic link API
      await new Promise((resolve) => setTimeout(resolve, 2000));
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
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,#1a2e1d,transparent_40%)] opacity-50" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom_right,#1a2e1d,transparent_40%)] opacity-50" />

      {/* Card */}
      <div className="relative z-10 w-full max-w-xl rounded-2xl bg-[#161616] p-8 shadow-lg">
        {/* Heading */}
        <h1 className="text-center text-3xl font-semibold text-white">
          Let&apos;s get you creating
        </h1>
        <p className="mt-1 text-center text-sm text-gray-400">
          Sign in or create an account in seconds — no password needed.
        </p>

        <form onSubmit={handleSubmit} className="mt-6">
          {/* Email input */}
          <div className="mt-6">
            <TextField
              label="Email"
              placeholder="Enter your email"
              type="email"
              className={`w-full rounded-lg border ${
                errors.email ? 'border-red-500' : 'border-transparent'
              } bg-[#2d2d2d] px-4 py-3 text-white placeholder-[#aaaca6] outline-none focus:border-green-500`}
              value={formData.email}
              onChange={(value) => handleInputChange('email', value)}
            />
            {errors.email && <p className="mt-1 text-sm text-red-500">{errors.email}</p>}
          </div>

          <Button
            type="submit"
            disabled={isLoading}
            className="mt-4 flex items-center justify-center space-x-2"
          >
            {isLoading ? (
              <>
                <div className="border-black h-5 w-5 animate-spin rounded-full border-2 border-t-transparent"></div>
                <span>Sending...</span>
              </>
            ) : (
              <>
                <Image src="/images/maginpan.svg" alt="maginpan" width={20} height={20} />
                <span>Send me the magic link</span>
              </>
            )}
          </Button>
        </form>

        {/* Divider */}
        <div className="my-4 flex items-center">
          <div className="h-px flex-grow bg-gray-700"></div>
          <span className="px-2 text-sm text-gray-500">or</span>
          <div className="h-px flex-grow bg-gray-700"></div>
        </div>

        {/* Google button */}
        <GoogleOAuthProvider clientId={env.NEXT_PUBLIC_GOOGLE_CLIENT_ID}>
          <GoogleAuthComponent />
        </GoogleOAuthProvider>
      </div>
    </div>
  );
}
