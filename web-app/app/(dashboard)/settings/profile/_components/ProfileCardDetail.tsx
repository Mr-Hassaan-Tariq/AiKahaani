'use client';

import { UserProfileType } from '@/(dashboard)/types';
import { FormProvider, useForm } from 'react-hook-form';

import { ProfileDetailFormType } from '../types';
import { Email_REGEX } from 'lib/constants';
import { logger } from 'lib/logger';
import FormInput from 'components/ui/FormInput';

export default function ProfileCardDetail({ profile }: { profile?: UserProfileType }) {
  const methods = useForm<ProfileDetailFormType>({
    defaultValues: {
      fullName: profile?.fullname || '',
      userName: profile?.username || '',
      email: profile?.email || '',
      language: profile?.preferred_language || '',
    },
  });

  const onSubmit = async (formData: ProfileDetailFormType) => {
    logger.info(formData);
  };

  return (
    <div className="rounded-xl border border-border bg-card p-6">
      <h3 className="mb-5 text-sm font-semibold text-foreground">Personal Details</h3>

      <FormProvider {...methods}>
        <form onSubmit={methods.handleSubmit(onSubmit)} className="flex flex-col gap-5">
          <div className="grid gap-4 sm:grid-cols-2">
            <FormInput
              disabled
              name="fullName"
              label="Full name"
              placeholder="Enter your full name"
              validationSchema={{
                required: 'Full name is required',
                minLength: { value: 3, message: 'Must be at least 3 characters' },
              }}
            />
            <FormInput
              disabled
              name="userName"
              label="Username"
              placeholder="Enter your username"
              validationSchema={{
                required: 'Username is required',
                minLength: { value: 3, message: 'Must be at least 3 characters' },
              }}
            />
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <FormInput
              disabled
              name="email"
              label="Email address"
              placeholder="Enter your email"
              validationSchema={{
                required: 'Email is required',
                pattern: { value: Email_REGEX, message: 'Invalid email address' },
              }}
            />
            <FormInput
              disabled
              name="language"
              label="Preferred language"
              placeholder="Enter your language"
              validationSchema={{ required: 'Language is required' }}
            />
          </div>
        </form>
      </FormProvider>
    </div>
  );
}
