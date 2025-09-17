'use client';

import { useState } from 'react';
import Image from 'next/image';
import { FormProvider, useForm } from 'react-hook-form';

import StyleSelector from './_components/StyleSelector';
import CopyIcon from '/public/images/copy.svg';
import EditIcon from '/public/images/edit.svg';
import InfoGrayIcon from '/public/images/info-gray.svg';
import InfoIcon from '/public/images/info.svg';
import MaginpanIcon from '/public/images/maginpan.svg';
import RefreshIcon from '/public/images/refresh.svg';
import Button from 'components/ui/Button';
import Card from 'components/ui/Card';
import Col from 'components/ui/Col';
import FormSelect from 'components/ui/FormSelect';
import FormTextarea from 'components/ui/FormTextArea';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';

export default function Page() {
  const [activeTab, setActiveTab] = useState<'generate' | 'optimize'>('generate');
  const [isLoading, setIsLoading] = useState(false);
  const [showTitles, setShowTitles] = useState(false);

  const methods = useForm({
    mode: 'onChange',
  });
  const {
    handleSubmit,
    watch,
    formState: { isValid },
  } = methods;

  const promptValue = watch('prompt');

  const onSubmit = (data: any) => {
    setIsLoading(true);
    console.log('Form Submitted:', data);
    setTimeout(() => setIsLoading(false), 2000);
    setShowTitles(true);
  };

  const titles = [
    '5 Productivity Hacks That Actually Work',
    'How to Stay Focused While Working From Home',
    '10 Morning Routines for Success',
    'Why Deep Work Increases Productivity',
    'Best Tools for Managing Remote Teams',
    'Habits That Make You More Effective',
  ];

  return (
    <Card className="mx-auto w-full max-w-[864px] px-4">
      <Col className="items-center">
        <Text className="text-center text-xl font-semibold text-white lg:text-[32px]">
          Title Generator
        </Text>
        <Text className="mt-1 text-center text-base text-[#AAACA6] lg:text-base">
          Generate or optimize YouTube titles with AI.
        </Text>

        <Row className="mt-1 flex w-full flex-col gap-2 sm:flex-row sm:justify-center">
          <button
            onClick={() => setActiveTab('generate')}
            className={`w-full rounded-[100px] px-[24px] py-[18px] font-bold transition-colors sm:w-auto ${
              activeTab === 'generate' ? 'bg-white text-black' : 'bg-[#2B2B2B] text-white'
            }`}
          >
            Generate New
          </button>
          <button
            onClick={() => setActiveTab('optimize')}
            className={`w-full rounded-[100px] px-[24px] py-[18px] font-bold transition-colors sm:w-auto ${
              activeTab === 'optimize' ? 'bg-white text-black' : 'bg-[#2B2B2B] text-white'
            }`}
          >
            Optimize Existing
          </button>
        </Row>

        {!showTitles && (
          <FormProvider {...methods}>
            <form onSubmit={handleSubmit(onSubmit)} className="mt-6 w-full">
              {activeTab === 'optimize' && (
                <Col className="mt-6 w-full justify-start gap-4">
                  <Text className="text-md mb-2 text-left text-white">
                    Script length & duration
                  </Text>

                  <Row className="flex flex-col items-start justify-start gap-4 lg:flex-row lg:gap-[200px]">
                    <label className="flex cursor-pointer items-center gap-2">
                      <input
                        type="radio"
                        value="saved"
                        {...methods.register('duration')}
                        className="peer h-6 w-6 cursor-pointer appearance-none rounded-full border-2 border-[#AAACA6] checked:border-white checked:bg-white checked:shadow-[inset_0_0_0_4px_#1E1E1E]"
                      />
                      <Text className="text-[16px] text-[#AAACA6] peer-checked:text-white">
                        Use a saved draft or script
                      </Text>
                    </label>

                    <label className="flex cursor-pointer items-center gap-2">
                      <input
                        type="radio"
                        value="manual"
                        {...methods.register('duration')}
                        className="peer h-6 w-6 cursor-pointer appearance-none rounded-full border-2 border-[#AAACA6] checked:border-white checked:bg-white checked:shadow-[inset_0_0_0_4px_#1E1E1E]"
                      />
                      <Text className="text-[16px] text-[#AAACA6] peer-checked:text-white">
                        Enter a title manually
                      </Text>
                    </label>
                  </Row>

                  {watch('duration') === 'saved' && (
                    <>
                      <Row className="mt-6 flex items-center justify-start gap-2">
                        <Text className="text-md mb-2 text-left text-white">
                          Select from a saved or draft script
                        </Text>
                        <Image
                          className="mt-[-8px]"
                          src={InfoIcon}
                          alt="info-icon"
                          width={16}
                          height={16}
                        />
                      </Row>

                      <FormSelect
                        name="scriptOption"
                        options={[
                          {
                            label: 'How to Stay Focused at Work',
                            value: 'draft1',
                            description: 'Learn 3 simple strategies to avoid distractions',
                          },
                          {
                            label: 'My Morning Routine (v2)',
                            value: 'draft2',
                            description: 'A short, energizing start to your day',
                          },
                          {
                            label: 'Boost Your Productivity with AI Tools',
                            value: 'draft3',
                            description: 'Discover how I save 10+ hours weekly using free AI tools',
                          },
                        ]}
                      />
                    </>
                  )}
                </Col>
              )}

              <Row className="mt-6 flex items-center justify-start gap-2">
                <Text className="text-md mb-2 text-left text-white">What’s your video about?</Text>
                <Image
                  className="mt-[-8px]"
                  src={InfoIcon}
                  alt="info-icon"
                  width={16}
                  height={16}
                />
              </Row>

              <FormTextarea
                name="prompt"
                placeholder="e.g. Top 5 productivity hacks that actually work..."
                validationSchema={{
                  required: 'Prompt is required',
                  minLength: {
                    value: 3,
                    message: 'Prompt must be at least 3 characters',
                  },
                }}
              />
              <Row>
                <Row className="flex items-center justify-start gap-2">
                  <Text className="text-md mb-2 mt-5 text-left text-white">Tone / Style</Text>
                  <Image
                    className="mt-[10px]"
                    src={InfoIcon}
                    alt="info-icon"
                    width={16}
                    height={16}
                  />
                </Row>
                <Row className="flex items-center justify-start gap-2">
                  <Image
                    className="mt-[10px]"
                    src={InfoGrayIcon}
                    alt="info-gray-icon"
                    width={16}
                    height={16}
                  />
                  <Text className="mb-2 mt-5 text-left text-[12px] font-semibold text-[#AAACA6]">
                    Recommended for your niche
                  </Text>
                </Row>
              </Row>

              <StyleSelector />

              <Button
                type="submit"
                disabled={!isValid || !promptValue || isLoading}
                className="mt-10 flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <>
                    <div className="h-5 w-5 animate-spin rounded-full border-2 border-black border-t-transparent"></div>
                    <span>Optimizing...</span>
                  </>
                ) : (
                  <>
                    <Image src={MaginpanIcon} alt="maginpan" width={20} height={20} />
                    <span className="font-bold">Optimize Title</span>
                  </>
                )}
              </Button>
            </form>
          </FormProvider>
        )}

        {showTitles && (
          <>
            <Row className="mb-6 mt-6 w-full">
              <Col
                className="flex max-h-[350px] w-full flex-col gap-3 overflow-y-auto pr-2"
                style={{
                  scrollbarWidth: 'none',
                  msOverflowStyle: 'none',
                }}
              >
                <style jsx>{`
                  div::-webkit-scrollbar {
                    display: none;
                  }
                `}</style>
                {titles.map((title, index) => (
                  <Row
                    key={index}
                    className="w-full items-center justify-between rounded-[16px] bg-[#FFFFFF1A] px-[12px] py-[16px]"
                  >
                    <Text className="text-md font-semibold text-white">
                      {index + 1}. {title}
                    </Text>
                    <Image
                      className="cursor-pointer"
                      src={CopyIcon}
                      alt="copy"
                      width={24}
                      height={24}
                    />
                  </Row>
                ))}
              </Col>
            </Row>
            <Row className="flex w-full gap-3">
              <button className="flex flex-1 items-center justify-center gap-2 rounded-[100px] bg-[#FFFFFF1A] py-[18px] backdrop-blur-[4px]">
                <Image src={EditIcon} alt="edit-icon" width={24} height={24} />
                <Text className="text-[16px] font-bold text-white">Edit Title Info</Text>
              </button>
              <button className="flex flex-1 items-center justify-center gap-2 rounded-[100px] bg-[#FFFFFF1A] py-[18px] backdrop-blur-[4px]">
                <Image src={RefreshIcon} alt="refresh-icon" width={24} height={24} />
                <Text className="text-[16px] font-bold text-white">Regenerate</Text>
              </button>
            </Row>
          </>
        )}
      </Col>
    </Card>
  );
}
