'use client';

import { useState } from 'react';
import Image from 'next/image';
import { Controller, FormProvider, useForm } from 'react-hook-form';

import { LoadingScreen } from './_components/LoadingScreen';
import StyleSelector from './_components/StyleSelector';
import CopyIcon from '/public/images/copy.svg';
import EditIcon from '/public/images/edit.svg';
import InfoGrayIcon from '/public/images/info-gray.svg';
import InfoIcon from '/public/images/info.svg';
import MaginpanIcon from '/public/images/maginpan.svg';
import RefreshIcon from '/public/images/refresh.svg';
import useGenerateTitles from 'lib/hooks/useGenerateTitles';
import useOptimizeTitles from 'lib/hooks/useOptimizeTitles';
import useToast from 'lib/utils/useToast';
import Button from 'components/ui/Button';
import Card from 'components/ui/Card';
import Col from 'components/ui/Col';
import FormInput from 'components/ui/FormInput';
import FormSelect from 'components/ui/FormSelect';
import FormTextArea from 'components/ui/FormTextArea_';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';

export default function Page() {
  const [activeTab, setActiveTab] = useState<'generate' | 'optimize'>('generate');
  const [showTitles, setShowTitles] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [titles, setTitles] = useState<string[]>([]);
  const [lastPayload, setLastPayload] = useState<any>(null);

  const generateTitles = useGenerateTitles();
  const optimizeTitles = useOptimizeTitles();
  const toast = useToast();

  const methods = useForm({
    defaultValues: {
      prompt: '',
      tones: [],
      duration: '',
      scriptOption: '',
    },
    mode: 'onChange',
  });

  const {
    control,
    handleSubmit,
    watch,
    formState: { isValid },
  } = methods;

  const onSubmit = async (data: any) => {
    setLastPayload({ ...data });
    setIsGenerating(true);

    try {
      let response;

      if (activeTab === 'optimize') {
        if (data.duration === 'saved') {
          response = await optimizeTitles.mutateAsync({
            prompt: data.prompt,
            tones: data.tones,
            script: data.scriptOption,
          });
        } else if (data.duration === 'manual') {
          response = await optimizeTitles.mutateAsync({
            prompt: data.prompt,
            tones: data.tones,
            user_title: data.manualTitle,
          });
        }
      } else {
        response = await generateTitles.mutateAsync({
          prompt: data.prompt,
          tones: data.tones,
        });
      }

      setTitles(response?.titles || []);
      setIsGenerating(false);
      setShowTitles(true);
      toast.success(
        'Success',
        `Titles ${activeTab === 'optimize' ? 'optimized' : 'generated'} successfully 🎉`,
      );
    } catch (err: any) {
      console.error('Error generating titles:', err);
      setIsGenerating(false);
      toast.error('Error', err.detail?.toString() || 'Something went wrong');
    }
  };

  const handleRegenerate = async () => {
    if (!lastPayload) return;

    setIsGenerating(true);
    try {
      let response;
      if (activeTab === 'optimize') {
        if (lastPayload.duration === 'saved') {
          response = await optimizeTitles.mutateAsync({
            prompt: lastPayload.prompt,
            tones: lastPayload.tones,
            script: lastPayload.scriptOption,
          });
        } else if (lastPayload.duration === 'manual') {
          response = await optimizeTitles.mutateAsync({
            prompt: lastPayload.prompt,
            tones: lastPayload.tones,
            user_title: lastPayload.manualTitle,
          });
        }
      } else {
        response = await generateTitles.mutateAsync({
          prompt: lastPayload.prompt,
          tones: lastPayload.tones,
        });
      }

      setTitles(response?.titles || []);
      setIsGenerating(false);
      toast.success(
        'Success',
        `Titles ${activeTab === 'optimize' ? 're-optimized' : 'regenerated'} successfully 🎉`,
      );
    } catch (err: any) {
      console.error('Error regenerating titles:', err);
      setIsGenerating(false);
      toast.error('Error', err.detail?.toString() || 'Something went wrong');
    }
  };

  const handleCopy = async (title: string) => {
    try {
      await navigator.clipboard.writeText(title);
      toast.success('Copied!', 'Title copied to clipboard 📋');
    } catch (err) {
      console.error('Failed to copy:', err);
      toast.error('Error', 'Failed to copy title');
    }
  };

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
            onClick={() => {
              setActiveTab('generate');
              setShowTitles(false);
            }}
            className={`w-full rounded-[100px] px-[24px] py-[18px] font-bold transition-colors sm:w-auto ${
              activeTab === 'generate' ? 'bg-white text-black' : 'bg-[#2B2B2B] text-white'
            }`}
          >
            Generate New
          </button>
          <button
            onClick={() => {
              setActiveTab('optimize');
              setShowTitles(false);
            }}
            className={`w-full rounded-[100px] px-[24px] py-[18px] font-bold transition-colors sm:w-auto ${
              activeTab === 'optimize' ? 'bg-white text-black' : 'bg-[#2B2B2B] text-white'
            }`}
          >
            Optimize Existing
          </button>
        </Row>

        {!showTitles && (
          <FormProvider {...methods}>
            {isGenerating ? (
              <LoadingScreen />
            ) : (
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
                              value: 'e2f9c4d1-91a2-4f7b-83a5-1234567890ab',
                              description: 'Learn 3 simple strategies to avoid distractions',
                            },
                            {
                              label: 'My Morning Routine (v2)',
                              value: 'a5b8e7c3-44de-4bc2-8b7f-abcdef123456',
                              description: 'A short, energizing start to your day',
                            },
                            {
                              label: 'Boost Your Productivity with AI Tools',
                              value: '9c7d8e1a-22fa-4dd6-9b99-9876543210ff',
                              description:
                                'Discover how I save 10+ hours weekly using free AI tools',
                            },
                          ]}
                        />
                      </>
                    )}
                  </Col>
                )}

                {watch('duration') === 'manual' && (
                  <>
                    <Row className="mt-6 flex items-center justify-start gap-2">
                      <Text className="text-md mb-2 text-left text-white">
                        Enter your title manually
                      </Text>
                      <Image
                        className="mt-[-8px]"
                        src={InfoIcon}
                        alt="info-icon"
                        width={16}
                        height={16}
                      />
                    </Row>

                    <FormInput
                      name="manualTitle"
                      placeholder="Enter your title manually..."
                      validationSchema={{
                        required: 'Title is required when entering manually',
                        minLength: {
                          value: 5,
                          message: 'Title must be at least 5 characters',
                        },
                      }}
                    />
                  </>
                )}

                <Row className="mt-6 flex items-center justify-start gap-2">
                  <Text className="text-md mb-2 text-left text-white">
                    What’s your video about?
                  </Text>
                  <Image
                    className="mt-[-8px]"
                    src={InfoIcon}
                    alt="info-icon"
                    width={16}
                    height={16}
                  />
                </Row>

                <FormTextArea
                  name="prompt"
                  placeholder="e.g. Top 5 productivity hacks that actually work..."
                  validationSchema={{
                    required: 'Prompt is required',
                    minLength: {
                      value: 30,
                      message: 'Prompt must be at least 30 characters',
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

                <Controller
                  name="tones"
                  control={control}
                  rules={{
                    required: 'Please select at least one tone',
                    validate: (val) =>
                      (val.length > 0 && val.length <= 3) || 'Select between 1 and 3 tones',
                  }}
                  render={({ field, fieldState }) => (
                    <StyleSelector
                      value={field.value}
                      onChange={field.onChange}
                      error={fieldState.error?.message}
                    />
                  )}
                />

                <Button
                  type="submit"
                  disabled={!isValid || isGenerating}
                  className="mt-10 flex items-center justify-center gap-2"
                >
                  {isGenerating ? (
                    <>
                      <div className="h-5 w-5 animate-spin rounded-full border-2 border-black border-t-transparent"></div>
                      <span> {activeTab === 'optimize' ? 'Optimizing...' : 'Generating...'}</span>
                    </>
                  ) : (
                    <>
                      <Image src={MaginpanIcon} alt="maginpan" width={20} height={20} />
                      <span className="font-bold">
                        {activeTab === 'optimize' ? 'Optimize Title' : 'Generate Title'}
                      </span>
                    </>
                  )}
                </Button>
              </form>
            )}
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
                      onClick={() => handleCopy(title)}
                    />
                  </Row>
                ))}
              </Col>
            </Row>
            <Row className="flex w-full gap-3">
              <button
                onClick={() => setShowTitles(false)}
                className="flex flex-1 items-center justify-center gap-2 rounded-[100px] bg-[#FFFFFF1A] py-[18px] backdrop-blur-[4px]"
              >
                <Image src={EditIcon} alt="edit-icon" width={24} height={24} />
                <Text className="text-[16px] font-bold text-white">Edit Title Info</Text>
              </button>
              <button
                onClick={handleRegenerate}
                disabled={isGenerating}
                className="flex flex-1 items-center justify-center gap-2 rounded-[100px] bg-[#FFFFFF1A] py-[18px] backdrop-blur-[4px]"
              >
                {isGenerating ? (
                  <>
                    <div className="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                    <Text className="text-[16px] font-bold text-white">Regenerating...</Text>
                  </>
                ) : (
                  <>
                    <Image src={RefreshIcon} alt="refresh-icon" width={24} height={24} />
                    <Text className="text-[16px] font-bold text-white">Regenerate</Text>
                  </>
                )}
              </button>
            </Row>
          </>
        )}
      </Col>
    </Card>
  );
}
