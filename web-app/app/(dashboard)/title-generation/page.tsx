'use client';

import { useEffect, useState } from 'react';
import Image from 'next/image';
import { FormProvider, useForm } from 'react-hook-form';

import ActionButtons from './_components/ActionButtons';
import { LoadingScreen } from './_components/LoadingScreen';
import OptimizeFormFields from './_components/OptimizeFormFields';
import PromptInput from './_components/PromptInput';
import Tabs from './_components/Tabs';
import TitleList from './_components/TitleList';
import ToneSelector from './_components/ToneSelector';
import InfoGrayIcon from '/public/images/info-gray.svg';
import InfoIcon from '/public/images/info.svg';
import MaginpanIcon from '/public/images/maginpan.svg';
import useGenerateTitles from 'lib/hooks/useGenerateTitles';
import useGetScripts from 'lib/hooks/useGetScripts';
import useOptimizeTitles from 'lib/hooks/useOptimizeTitles';
import useToast from 'lib/utils/useToast';
import Button from 'components/ui/Button';
import Card from 'components/ui/Card';
import Col from 'components/ui/Col';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';

export default function Page() {
  const [activeTab, setActiveTab] = useState<'generate' | 'optimize'>('generate');
  const [showTitles, setShowTitles] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [titles, setTitles] = useState<string[]>([]);
  const [lastPayload, setLastPayload] = useState<any>(null);

  const { data: script } = useGetScripts();
  const generateTitles = useGenerateTitles();
  const optimizeTitles = useOptimizeTitles();
  const toast = useToast();

  // Adjust validation logic for the form
  const methods = useForm({
    defaultValues: { prompt: '', tones: [], duration: 'saved', scriptOption: '', manualTitle: '' },
    mode: 'onChange',
    resolver: async (data) => {
      const errors: any = {};

      // Description is required
      if (!data.prompt) {
        errors.prompt = 'Description is required';
      }

      // At least one tone is required
      if (!data.tones || data.tones.length === 0) {
        errors.tones = 'At least one tone is required';
      }

      if (activeTab === 'optimize') {
        // Validation for "saved" duration
        if (data.duration === 'saved' && !data.scriptOption) {
          errors.scriptOption = 'Script selection is required';
        }

        // Validation for "manual" duration
        if (data.duration === 'manual' && !data.manualTitle) {
          errors.manualTitle = 'Manual title is required';
        }
      }

      return { values: data, errors };
    },
  });
  const {
    control,
    handleSubmit,
    watch,
    formState: { isValid },
    register,
    reset,
  } = methods;

  useEffect(() => {
    reset();
  }, [activeTab]);
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
        <Text className="mt-1 text-center text-base text-[#AAACA6]">
          Generate or optimize YouTube titles with AI.
        </Text>

        <Tabs activeTab={activeTab} setActiveTab={setActiveTab} />

        {!showTitles ? (
          <FormProvider {...methods}>
            {isGenerating ? (
              <LoadingScreen />
            ) : (
              <form onSubmit={handleSubmit(onSubmit)} className="mt-6 w-full">
                {activeTab === 'optimize' && (
                  <OptimizeFormFields watch={watch} scripts={script?.results} register={register} />
                )}
                <PromptInput />
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

                <ToneSelector control={control} />

                <p className="text-left text-white">isGenerating: {isGenerating.toString()}</p>
                <Button
                  type="submit"
                  disabled={!isValid || isGenerating}
                  className="mt-10 flex items-center justify-center gap-2"
                >
                  {isGenerating ? (
                    <>
                      <div className="w-5 animate-spin rounded-full border-2 border-black border-t-transparent"></div>
                      <span>{activeTab === 'optimize' ? 'Optimizing...' : 'Generating...'}</span>
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
        ) : (
          <>
            <TitleList titles={titles} onCopy={handleCopy} />
            <ActionButtons
              isGenerating={isGenerating}
              onEdit={() => setShowTitles(false)}
              onRegenerate={handleRegenerate}
            />
          </>
        )}
      </Col>
    </Card>
  );
}
