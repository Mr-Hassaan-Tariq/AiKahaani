'use client';

import { useEffect, useState } from 'react';
import { FormProvider, useForm } from 'react-hook-form';
import { Wand2 } from 'lucide-react';

import ActionButtons from './_components/ActionButtons';
import { LoadingScreen } from './_components/LoadingScreen';
import OptimizeFormFields from './_components/OptimizeFormFields';
import PromptInput from './_components/PromptInput';
import Tabs from './_components/Tabs';
import TitleList from './_components/TitleList';
import ToneSelector from './_components/ToneSelector';
import useGenerateTitles from 'lib/hooks/useGenerateTitles';
import useGetScripts from 'lib/hooks/useGetScripts';
import useOptimizeTitles from 'lib/hooks/useOptimizeTitles';
import useToast from 'lib/utils/useToast';
import { Button } from 'components/ui/Button';

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

  const methods = useForm({
    defaultValues: { prompt: '', tones: [], duration: 'saved', scriptOption: '', manualTitle: '' },
    mode: 'onChange',
    resolver: async (data) => {
      const errors: any = {};
      if (!data.prompt) errors.prompt = 'Description is required';
      if (!data.tones || data.tones.length === 0) errors.tones = 'At least one tone is required';
      if (activeTab === 'optimize') {
        if (data.duration === 'saved' && !data.scriptOption) errors.scriptOption = 'Script selection is required';
        if (data.duration === 'manual' && !data.manualTitle) errors.manualTitle = 'Manual title is required';
      }
      return { values: data, errors };
    },
  });

  const { control, handleSubmit, watch, formState: { isValid }, register, reset, resetField, setValue } = methods;

  useEffect(() => {
    reset({ prompt: '', tones: [], duration: 'saved', scriptOption: '', manualTitle: '' }, { keepErrors: false });
  }, [activeTab]); // eslint-disable-line react-hooks/exhaustive-deps

  const onSubmit = async (data: any) => {
    const hasShocking = data.tones.includes('Shocking');
    const hasMysterious = data.tones.includes('Mysterious');
    const hasNeutral = data.tones.includes('Neutral');

    if ((hasShocking && hasMysterious) || (hasShocking && hasNeutral)) {
      toast.error(
        'Conflicting tones',
        hasShocking && hasMysterious
          ? '"Shocking" and "Mysterious" together may confuse your audience.'
          : '"Shocking" and "Neutral" create an inconsistent mood.',
      );
      return;
    }

    setLastPayload({ ...data });
    setIsGenerating(true);

    try {
      let response;
      if (activeTab === 'optimize') {
        response = await optimizeTitles.mutateAsync(
          data.duration === 'saved'
            ? { prompt: data.prompt, tones: data.tones, script: data.scriptOption }
            : { prompt: data.prompt, tones: data.tones, user_title: data.manualTitle },
        );
      } else {
        response = await generateTitles.mutateAsync({ prompt: data.prompt, tones: data.tones });
      }

      setTitles(response?.titles || []);
      setIsGenerating(false);
      setShowTitles(true);
      toast.success('Success', `Titles ${activeTab === 'optimize' ? 'optimized' : 'generated'} successfully`);
    } catch (err: any) {
      setIsGenerating(false);
      if (err?.prompt?.[0]) { toast.error('Validation Error', err.prompt[0]); return; }
      if (err?.detail) { toast.error('Error', err.detail.toString()); return; }
      toast.error('Error', 'Something went wrong while processing your request.');
    }
  };

  const handleRegenerate = async () => {
    if (!lastPayload) return;
    setIsGenerating(true);
    try {
      let response;
      if (activeTab === 'optimize') {
        response = await optimizeTitles.mutateAsync(
          lastPayload.duration === 'saved'
            ? { prompt: lastPayload.prompt, tones: lastPayload.tones, script: lastPayload.scriptOption }
            : { prompt: lastPayload.prompt, tones: lastPayload.tones, user_title: lastPayload.manualTitle },
        );
      } else {
        response = await generateTitles.mutateAsync({ prompt: lastPayload.prompt, tones: lastPayload.tones });
      }
      setTitles(response?.titles || []);
      setIsGenerating(false);
      toast.success('Success', `Titles ${activeTab === 'optimize' ? 're-optimized' : 'regenerated'} successfully`);
    } catch (err: any) {
      setIsGenerating(false);
      toast.error('Error', err?.detail?.toString() || 'Something went wrong');
    }
  };

  const handleCopy = async (title: string) => {
    try {
      await navigator.clipboard.writeText(title);
      toast.success('Copied!', 'Title copied to clipboard');
    } catch {
      toast.error('Error', 'Failed to copy title');
    }
  };

  return (
    <div className="flex flex-col">
      <div className="mx-auto w-full max-w-2xl px-6 py-8">
        <Tabs activeTab={activeTab} setActiveTab={setActiveTab} isGenerating={isGenerating} />

        {!showTitles ? (
          <FormProvider {...methods}>
            {isGenerating ? (
              <LoadingScreen />
            ) : (
              <form onSubmit={handleSubmit(onSubmit)} className="mt-6 flex flex-col gap-5">
                {activeTab === 'optimize' && (
                  <OptimizeFormFields
                    watch={watch}
                    scripts={script?.results}
                    register={register}
                    resetField={resetField}
                    setValue={setValue}
                  />
                )}

                <PromptInput />

                <div>
                  <div className="mb-2 flex items-center justify-between">
                    <span className="text-sm font-medium text-foreground">Tone / Style</span>
                    <span className="text-xs text-muted-foreground">Pick 1–3 tones</span>
                  </div>
                  <ToneSelector control={control} />
                </div>

                <Button type="submit" size="lg" className="w-full" disabled={!isValid || isGenerating} loading={isGenerating}>
                  <Wand2 className="h-4 w-4" />
                  {activeTab === 'optimize' ? 'Optimize Title' : 'Generate Titles'}
                </Button>
              </form>
            )}
          </FormProvider>
        ) : (
          <div className="mt-6 flex flex-col gap-5">
            <TitleList titles={titles} onCopy={handleCopy} />
            <ActionButtons isGenerating={isGenerating} onEdit={() => setShowTitles(false)} onRegenerate={handleRegenerate} />
          </div>
        )}
      </div>
    </div>
  );
}
