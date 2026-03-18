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
    <FormProvider {...methods}>
      <form onSubmit={methods.handleSubmit(onSubmit)} className="contents">

        {/* Personal Details card */}
        <div className="rounded-xl border border-border bg-card p-8">
          <h3 className="text-[18px] font-semibold text-foreground pb-6 mb-6 border-b border-border">
            Personal Details
          </h3>
          <div className="flex flex-col gap-6">
            <div className="grid gap-6 sm:grid-cols-2">
              <FormInput
                disabled
                name="fullName"
                label="Full Name"
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
            <FormInput
              disabled
              name="email"
              label="Email Address"
              placeholder="Enter your email"
              validationSchema={{
                required: 'Email is required',
                pattern: { value: Email_REGEX, message: 'Invalid email address' },
              }}
            />
            <FormInput
              disabled
              name="language"
              label="Preferred Language"
              placeholder="Enter your language"
              validationSchema={{ required: 'Language is required' }}
            />
          </div>
        </div>

        {/* Channel Details card */}
        <div className="rounded-xl border border-border bg-card p-8">
          <h3 className="text-[18px] font-semibold text-foreground pb-6 mb-6 border-b border-border">
            Channel Details
          </h3>
          <div className="flex flex-col gap-6">
            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-semibold text-foreground">YouTube Channel Name</label>
              <input
                disabled
                placeholder="Your channel name…"
                className="h-10 w-full rounded-md border border-border bg-input px-3 text-sm text-foreground placeholder:text-muted-foreground opacity-60 cursor-not-allowed focus:outline-none"
              />
            </div>
            <div className="grid gap-6 sm:grid-cols-2">
              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-semibold text-foreground">Primary Niche</label>
                <input
                  disabled
                  placeholder="e.g. Education / Productivity"
                  className="h-10 w-full rounded-md border border-border bg-input px-3 text-sm text-foreground placeholder:text-muted-foreground opacity-60 cursor-not-allowed focus:outline-none"
                />
              </div>
              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-semibold text-foreground">Target Audience Language</label>
                <input
                  disabled
                  placeholder="e.g. English (US)"
                  className="h-10 w-full rounded-md border border-border bg-input px-3 text-sm text-foreground placeholder:text-muted-foreground opacity-60 cursor-not-allowed focus:outline-none"
                />
              </div>
            </div>
          </div>
        </div>

      </form>
    </FormProvider>
  );
}
