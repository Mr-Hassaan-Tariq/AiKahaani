'use client';

import { UserProfileType } from '@/(dashboard)/types';
import { FormProvider, useForm } from 'react-hook-form';

import { ProfileDetailFormType } from '../types';
import { Email_REGEX } from 'lib/constants';
import { logger } from 'lib/logger';
import Card from 'components/ui/Card';
import Col from 'components/ui/Col';
import FormInput from 'components/ui/FormInput';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';

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
    <Card>
      <FormProvider {...methods}>
        <form onSubmit={methods.handleSubmit(onSubmit)}>
          <Col className="gap-6 lg:gap-8">
            <Text variant="2xl" className="text-xl text-white lg:text-2xl">
              Personal details
            </Text>

            <Row className="flex-col gap-4 md:gap-6 lg:flex-row">
              <FormInput
                disabled
                name="fullName"
                label="Full name"
                placeholder="Enter your full name"
                validationSchema={{
                  required: 'Full name is required',
                  minLength: { value: 3, message: 'Full name must be at least 3 characters' },
                }}
              />
              <FormInput
                disabled
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
                disabled
                name="email"
                label="Email address"
                placeholder="Enter your email address"
                validationSchema={{
                  required: 'Email is required',
                  pattern: { value: Email_REGEX, message: 'Invalid email address' },
                }}
              />
              <FormInput
                disabled
                name="language"
                label="Preferred language"
                placeholder="Enter your preferred language"
                validationSchema={{
                  required: 'Language is required',
                }}
              />
            </Row>

            {/* <Button
              type="submit"
              disabled={!isDirty || !isValid || isUpdating}
              className="ml-auto lg:max-w-28"
            >
              {isUpdating ? 'Saving...' : 'Save'}
            </Button>

            {successMessage && (
              <p className="mt-2 font-semibold text-green-500">{successMessage}</p>
            )} */}
          </Col>
        </form>
      </FormProvider>
    </Card>
  );
}
