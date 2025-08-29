'use client';

import { FormProvider, useForm } from 'react-hook-form';

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
  } = methods;

  function onSubmit(formData: ProfileDetailFormType) {
    console.warn(formData);
  }

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
                name="fullName"
                label="Full name"
                placeholder="Enter your full name"
                validationSchema={{
                  required: 'Full name is required',
                  minLength: {
                    value: 3,
                    message: 'Full name must be longer than or equal to 3 characters',
                  },
                }}
              />
              <FormInput
                name="userName"
                label="Username"
                placeholder="Enter your username"
                validationSchema={{
                  required: 'User name is required',
                  minLength: {
                    value: 3,
                    message: 'User name must be longer than or equal to 3 characters',
                  },
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
                  pattern: {
                    value: Email_REGEX,
                    message: 'Invalid email address',
                  },
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
              disabled={!isDirty || !isValid}
              className="ml-auto w-full rounded-full bg-gradient-to-r from-[#2BFF13] to-[#20BF0E] p-3 font-semibold text-black hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50 lg:max-w-28"
            >
              Save
            </Button>
          </Col>
        </form>
      </FormProvider>
    </Card>
  );
}
