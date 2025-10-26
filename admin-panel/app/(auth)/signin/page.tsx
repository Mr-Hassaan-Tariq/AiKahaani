'use client';

import { useState } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import * as yup from 'yup';

import MaginpanIcon from '/public/images/maginpan.svg';
import { authService } from 'lib/api';
import Button from 'components/common/Button';
import TextField from 'components/common/TextField';

// Yup validation schema
const loginSchema = yup.object({
  email: yup
    .string()
    .required('Email is required')
    .email('Please enter a valid email address')
    .trim(),
  password: yup
    .string()
    .required('Password is required')
    .min(6, 'Password must be at least 6 characters'),
});

type LoginFormData = yup.InferType<typeof loginSchema>;

export default function AdminLogin() {
  const router = useRouter();
  const [formData, setFormData] = useState<LoginFormData>({
    email: '',
    password: '',
  });
  const [errors, setErrors] = useState<Partial<LoginFormData>>({});
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // Handle input change
  const handleInputChange = (field: keyof LoginFormData, value: string) => {
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
      await loginSchema.validate(formData, { abortEarly: false });

      const response = await authService.adminLogin(formData.email, formData.password);

      if (response.success) {
        router.push('/');
      }
    } catch (validationError) {
      if (validationError instanceof yup.ValidationError) {
        // Convert Yup errors to our format
        const yupErrors: Partial<LoginFormData> = {};
        validationError.inner.forEach((error) => {
          if (error.path) {
            yupErrors[error.path as keyof LoginFormData] = error.message;
          }
        });
        setErrors(yupErrors);
      } else {
        // Handle other errors
        setErrors({ email: 'Invalid email or password. Please try again.' });
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
        <h1 className="text-center text-4xl font-bold text-white">Admin Login</h1>
        <p className="mt-2 text-center text-lg text-gray-400">
          Sign in to your admin account <br></br> to access the dashboard.
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

          {/* Password input */}
          <div className="mt-6">
            <TextField
              label="Password"
              placeholder="Enter your password"
              type="password"
              className={`w-full rounded-xl border ${
                errors.password ? 'border-red-500' : 'border-transparent'
              } bg-[#2d2d2d] px-4 py-3 text-white placeholder-[#aaaca6] outline-none focus:border-green-500`}
              value={formData.password}
              onChange={(value) => handleInputChange('password', value)}
            />
            {errors.password && <p className="mt-1 text-sm text-red-500">{errors.password}</p>}
          </div>

          <Button type="submit" disabled={isLoading} className="mt-10">
            {isLoading ? (
              <>
                <div className="h-5 w-5 animate-spin rounded-full border-2 border-black border-t-transparent"></div>
                <span>Signing in...</span>
              </>
            ) : (
              <>
                <Image src={MaginpanIcon} alt="maginpan" width={20} height={20} />
                <span className="font-bold"> Sign In</span>
              </>
            )}
          </Button>
        </form>
      </div>
    </div>
  );
}
