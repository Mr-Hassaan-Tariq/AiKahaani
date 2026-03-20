'use client';

import { useState } from 'react';
import { updateUserProfile } from '@/(dashboard)/actions';
import { UserProfileType } from '@/(dashboard)/types';
import { FormProvider, useForm } from 'react-hook-form';
import { toast } from 'sonner';

import { ProfileDetailFormType } from '../types';
import { Email_REGEX } from 'lib/constants';
import { Button } from 'components/ui/Button';
import FormInput from 'components/ui/FormInput';

export default function ProfileCardDetail({ profile }: { profile?: UserProfileType }) {
  const [isSaving, setIsSaving] = useState(false);

  const methods = useForm<ProfileDetailFormType>({
    defaultValues: {
      fullName: profile?.fullname || '',
      userName: profile?.username || '',
      email: profile?.email || '',
      language: profile?.preferred_language || '',
    },
  });

  const {
    handleSubmit,
    reset,
    formState: { isDirty },
  } = methods;

  const onSubmit = async (formData: ProfileDetailFormType) => {
    setIsSaving(true);
    try {
      const result = await updateUserProfile({
        fullname: formData.fullName,
        username: formData.userName,
        preferred_language: formData.language,
      });

      if (result.isError) {
        toast.error('Failed to save', { description: result.error?.message || 'Unknown error' });
        return;
      }

      toast.success('Profile saved');
      reset(formData);
    } catch {
      toast.error('Failed to save', { description: 'Something went wrong' });
    } finally {
      setIsSaving(false);
    }
  };

  const handleDiscard = () => {
    reset();
  };

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmit)} className="contents">
        {/* Personal Details card */}
        <div className="rounded-xl border border-border bg-card p-4 sm:p-8">
          <h3 className="mb-6 border-b border-border pb-6 text-[18px] font-semibold text-foreground">
            Personal Details
          </h3>
          <div className="flex flex-col gap-6">
            <div className="grid gap-6 sm:grid-cols-2">
              <FormInput
                name="fullName"
                label="Full Name"
                placeholder="Enter your full name"
                validationSchema={{
                  required: 'Full name is required',
                  minLength: { value: 3, message: 'Must be at least 3 characters' },
                }}
              />
              <FormInput
                name="userName"
                label="Username"
                placeholder="Enter your username"
                validationSchema={{
                  required: 'Username is required',
                  minLength: { value: 3, message: 'Must be at least 3 characters' },
                  pattern: { value: /^\S+$/, message: 'Username cannot contain spaces' },
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
              name="language"
              label="Preferred Language"
              placeholder="e.g. en"
              validationSchema={{ required: 'Language is required' }}
            />
          </div>
        </div>

        {/* Channel Details card */}
        <div className="rounded-xl border border-border bg-card p-4 sm:p-8">
          <h3 className="mb-6 border-b border-border pb-6 text-[18px] font-semibold text-foreground">
            Channel Details
          </h3>
          <div className="flex flex-col gap-6">
            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-semibold text-foreground">YouTube Channel Name</label>
              <input
                disabled
                placeholder="Your channel name…"
                className="h-10 w-full cursor-not-allowed rounded-md border border-border bg-input px-3 text-sm text-foreground opacity-60 placeholder:text-muted-foreground focus:outline-none"
              />
            </div>
            <div className="grid gap-6 sm:grid-cols-2">
              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-semibold text-foreground">Primary Niche</label>
                <input
                  disabled
                  placeholder="e.g. Education / Productivity"
                  className="h-10 w-full cursor-not-allowed rounded-md border border-border bg-input px-3 text-sm text-foreground opacity-60 placeholder:text-muted-foreground focus:outline-none"
                />
              </div>
              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-semibold text-foreground">
                  Target Audience Language
                </label>
                <input
                  disabled
                  placeholder="e.g. English (US)"
                  className="h-10 w-full cursor-not-allowed rounded-md border border-border bg-input px-3 text-sm text-foreground opacity-60 placeholder:text-muted-foreground focus:outline-none"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Footer actions */}
        <div className="flex items-center justify-end gap-3 pb-4 pt-2">
          <Button
            type="button"
            variant="outline"
            onClick={handleDiscard}
            disabled={!isDirty || isSaving}
          >
            Discard Changes
          </Button>
          <Button
            type="submit"
            variant="primary"
            disabled={!isDirty || isSaving}
            loading={isSaving}
          >
            Save Profile
          </Button>
        </div>
      </form>
    </FormProvider>
  );
}
