'use client';

import { useEffect, useState } from 'react';
import { FormProvider, useForm } from 'react-hook-form';

import { userService } from 'lib/api';
import { Email_REGEX } from 'lib/constants';
import Card from 'components/ui/Card';
import Col from 'components/ui/Col';
import FormInput from 'components/ui/FormInput';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';
import Button from 'components/common/Button';

interface ProfileDetailFormType {
  fullName: string;
  userName: string;
  email: string;
  language: string;
}

export default function ProfileCardDetail() {
  const methods = useForm<ProfileDetailFormType>({
    defaultValues: {
      fullName: '',
      userName: '',
      email: '',
      language: '',
    },
  });

  const {
    formState: { isDirty, isValid },
    reset,
  } = methods;

  const [isFetching, setIsFetching] = useState<boolean>(true);
  const [isUpdating, setIsUpdating] = useState<boolean>(false);
  const [successMessage, setSuccessMessage] = useState<string>('');

  // Fetch user details on component mount
  useEffect(() => {
    async function fetchDetails() {
      try {
        setIsFetching(true);
        const user = await userService.getUserDetails();
        reset({
          fullName: user.fullname ?? '',
          userName: user.username ?? '',
          email: user.email ?? '',
          language: (user as any).preferred_language === 'en' ? 'English' : '',
        });
      } catch (err: any) {
        console.error('Failed to fetch user details', err);
      } finally {
        setIsFetching(false);
      }
    }
    fetchDetails();
  }, [reset]);

  // Submit form to update user details
  const onSubmit = async (formData: ProfileDetailFormType) => {
    try {
      setIsUpdating(true);
      const payload = {
        fullname: formData.fullName,
        username: formData.userName,
        email: formData.email,
        preferred_language: formData.language,
      };

      const updatedUser = await userService.updateUserDetails(payload);
      console.log('Updated User Details:', updatedUser);

      // Reset form with updated values
      reset({
        fullName: updatedUser.fullname ?? '',
        userName: updatedUser.username ?? '',
        email: updatedUser.email ?? '',
        language: updatedUser.preferred_language ?? '',
      });

      // Show success message
      setSuccessMessage('Profile updated successfully!');
      setTimeout(() => setSuccessMessage(''), 3000); // hide after 3s
    } catch (err: any) {
      console.error('Failed to update user details', err);
      alert(err.message || 'Failed to update profile');
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <Card>
      <FormProvider {...methods}>
        <form onSubmit={methods.handleSubmit(onSubmit)}>
          <Col className="gap-6 lg:gap-8">
            <Text variant="2xl" className="text-xl text-white lg:text-2xl">
              Personal details
            </Text>

            {isFetching ? (
              <p className="text-gray-400">Loading user details...</p>
            ) : (
              <>
                <Row className="flex-col gap-4 md:gap-6 lg:flex-row">
                  <FormInput
                    name="fullName"
                    label="Full name"
                    placeholder="Enter your full name"
                    validationSchema={{
                      required: 'Full name is required',
                      minLength: { value: 3, message: 'Full name must be at least 3 characters' },
                    }}
                  />
                  <FormInput
                    name="userName"
                    label="Username"
                    placeholder="Enter your username"
                    validationSchema={{
                      required: 'User name is required',
                      minLength: { value: 3, message: 'User name must be at least 3 characters' },
                    }}
                  />
                </Row>
                <Row className="flex-col gap-4 md:gap-6 lg:flex-row">
                  <FormInput
                    name="email"
                    label="Email address"
                    placeholder="Enter your email address"
                    validationSchema={{
                      required: 'Email is required',
                      pattern: { value: Email_REGEX, message: 'Invalid email address' },
                    }}
                  />
                  <FormInput
                    name="language"
                    label="Preferred language"
                    placeholder="Enter your preferred language"
                    validationSchema={{
                      required: 'Language is required',
                    }}
                  />
                </Row>

                <Button
                  type="submit"
                  disabled={!isDirty || !isValid || isUpdating}
                  className="ml-auto w-full rounded-full bg-gradient-to-r from-[#2BFF13] to-[#20BF0E] p-3 font-semibold text-black hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50 lg:max-w-28"
                >
                  {isUpdating ? 'Saving...' : 'Save'}
                </Button>

                {successMessage && (
                  <p className="mt-2 font-semibold text-green-500">{successMessage}</p>
                )}
              </>
            )}
          </Col>
        </form>
      </FormProvider>
    </Card>
  );
}
