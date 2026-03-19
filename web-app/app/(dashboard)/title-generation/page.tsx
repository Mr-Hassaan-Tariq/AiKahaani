'use client';

import { useEffect, useState } from 'react';
import { RefreshCw, Sparkles, Youtube } from 'lucide-react';
import { FormProvider, useForm } from 'react-hook-form';

import { LoadingScreen } from './_components/LoadingScreen';
import OptimizeFormFields from './_components/OptimizeFormFields';
import PromptInput from './_components/PromptInput';
import TitleList from './_components/TitleList';
import ToneSelector from './_components/ToneSelector';
import useGenerateTitles from 'lib/hooks/useGenerateTitles';
import useGetScripts from 'lib/hooks/useGetScripts';
import useOptimizeTitles from 'lib/hooks/useOptimizeTitles';
import { cn } from 'lib/utils';
import useToast from 'lib/utils/useToast';
import { Button } from 'components/ui/Button';

// ── Step card wrapper ─────────────────────────────────────────────────────────
function StepCard({
  number,
  title,
  description,
  badge,
  children,
}: {
  number: number;
  title: string;
  description: string;
  badge?: string;
  children: React.ReactNode;
}) {
  return (
    <section className="relative flex flex-col gap-5 overflow-hidden rounded-xl border border-border bg-card p-4 sm:p-7">
      {/* top accent gradient line */}
      <div className="absolute left-0 right-0 top-0 h-px bg-gradient-to-r from-transparent via-primary/30 to-transparent" />

      <div className="flex items-start gap-4">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-bold text-primary">
          {number}
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-3">
            <h2 className="text-[18px] font-semibold leading-snug tracking-tight text-foreground sm:text-[22px]">
              {title}
            </h2>
            {badge && (
              <span className="hidden shrink-0 items-center gap-1.5 whitespace-nowrap rounded-full bg-secondary px-3 py-1.5 text-xs font-medium text-muted-foreground sm:inline-flex">
                {badge}
              </span>
            )}
          </div>
          <p className="mt-1 text-sm leading-relaxed text-muted-foreground">{description}</p>
          {badge && (
            <span className="mt-2 inline-flex items-center gap-1.5 rounded-full bg-secondary px-2.5 py-1 text-xs font-medium text-muted-foreground sm:hidden">
              {badge}
            </span>
          )}
        </div>
      </div>

      {children}
    </section>
  );
}

// ── Page ─────────────────────────────────────────────────────────────────────
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
        if (data.duration === 'saved' && !data.scriptOption)
          errors.scriptOption = 'Script selection is required';
        if (data.duration === 'manual' && !data.manualTitle)
          errors.manualTitle = 'Manual title is required';
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
    resetField,
    setValue,
  } = methods;

  useEffect(() => {
    reset(
      { prompt: '', tones: [], duration: 'saved', scriptOption: '', manualTitle: '' },
      { keepErrors: false },
    );
    setShowTitles(false);
    setTitles([]);
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
    setShowTitles(false);

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
      setShowTitles(true);
      toast.success(
        'Success',
        `Titles ${activeTab === 'optimize' ? 'optimized' : 'generated'} successfully`,
      );
    } catch (err: any) {
      if (err?.prompt?.[0]) {
        toast.error('Validation Error', err.prompt[0]);
        return;
      }
      if (err?.detail) {
        toast.error('Error', err.detail.toString());
        return;
      }
      toast.error('Error', 'Something went wrong while processing your request.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleRegenerate = async () => {
    if (!lastPayload) return;
    setIsGenerating(true);
    setShowTitles(false);
    try {
      let response;
      if (activeTab === 'optimize') {
        response = await optimizeTitles.mutateAsync(
          lastPayload.duration === 'saved'
            ? {
                prompt: lastPayload.prompt,
                tones: lastPayload.tones,
                script: lastPayload.scriptOption,
              }
            : {
                prompt: lastPayload.prompt,
                tones: lastPayload.tones,
                user_title: lastPayload.manualTitle,
              },
        );
      } else {
        response = await generateTitles.mutateAsync({
          prompt: lastPayload.prompt,
          tones: lastPayload.tones,
        });
      }
      setTitles(response?.titles || []);
      setShowTitles(true);
      toast.success(
        'Success',
        `Titles ${activeTab === 'optimize' ? 're-optimized' : 'regenerated'} successfully`,
      );
    } catch (err: any) {
      toast.error('Error', err?.detail?.toString() || 'Something went wrong');
    } finally {
      setIsGenerating(false);
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

  const stepOffset = activeTab === 'optimize' ? 1 : 0;

  return (
    <div className="px-4 py-6 sm:px-8 sm:py-10">
      <div className="mx-auto flex w-full max-w-[960px] flex-col gap-6">
        {/* ── Hero ── */}
        <div className="flex flex-col gap-4 pb-2">
          <div className="inline-flex w-fit items-center gap-2 rounded-full bg-primary/10 px-3 py-1.5 text-[13px] font-semibold text-primary">
            <Youtube className="h-3.5 w-3.5" />
            YouTube title workflow
          </div>
          <h1 className="text-[28px] font-bold leading-[1.15] tracking-tight text-foreground sm:text-[42px] sm:leading-[1.1]">
            Create scroll-stopping YouTube titles from a single topic.
          </h1>
          <p className="max-w-[680px] text-sm leading-relaxed text-muted-foreground sm:text-base">
            Start with your video idea, tune the title angle, then generate high-performing headline
            options in a step-by-step flow.
          </p>
          {/* Mode pills */}
          <div className="mt-1 flex items-center gap-3">
            {(['generate', 'optimize'] as const).map((tab) => (
              <button
                key={tab}
                type="button"
                onClick={() => setActiveTab(tab)}
                disabled={isGenerating}
                className={cn(
                  'whitespace-nowrap rounded-full px-4 py-2.5 text-sm font-medium transition-colors',
                  activeTab === tab
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
                  isGenerating && 'cursor-not-allowed opacity-50',
                )}
              >
                {tab === 'generate' ? 'Generate New' : 'Optimize Existing'}
              </button>
            ))}
          </div>
        </div>

        <FormProvider {...methods}>
          <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-6">
            {/* ── Optimize: script source (step 1 only when optimize tab) ── */}
            {activeTab === 'optimize' && (
              <StepCard
                number={1}
                title="Select your script or title"
                description="Choose a saved draft to optimize, or enter an existing title manually."
              >
                <OptimizeFormFields
                  watch={watch}
                  scripts={script?.data ?? (script as any)?.results}
                  register={register}
                  resetField={resetField}
                  setValue={setValue}
                />
              </StepCard>
            )}

            {/* ── Step 1 / 2: Topic prompt ── */}
            <StepCard
              number={1 + stepOffset}
              title="What is your video about?"
              description="Describe the topic, promise, and who the video is for. The richer the prompt, the stronger the title suggestions."
              badge="Topic-driven generation"
            >
              <PromptInput />
            </StepCard>

            {/* ── Step 2 / 3: Tone direction ── */}
            <StepCard
              number={2 + stepOffset}
              title="Choose title direction"
              description="Select the tone and framing style you want the AI to follow for this batch of titles."
            >
              <div>
                <div className="mb-2 flex items-center justify-between">
                  <span className="text-sm font-medium text-foreground">Tone / Style</span>
                  <span className="text-xs text-muted-foreground">Pick 1–3 tones</span>
                </div>
                <ToneSelector control={control} />
              </div>
            </StepCard>

            {/* ── Step 3 / 4: Generate ── */}
            <StepCard
              number={3 + stepOffset}
              title="Generate and review title options"
              description="Compare multiple options with different hooks, then copy the strongest one for your script project."
              badge={`${titles.length > 0 ? titles.length : 6} optimized results`}
            >
              {isGenerating ? (
                <LoadingScreen />
              ) : (
                <div className="flex flex-wrap items-center gap-3">
                  <Button type="submit" disabled={!isValid || isGenerating} loading={isGenerating}>
                    <Sparkles className="h-4 w-4" />
                    {activeTab === 'optimize' ? 'Optimize Title' : 'Generate 6 Titles'}
                  </Button>
                  {showTitles && (
                    <Button
                      type="button"
                      variant="outline"
                      onClick={handleRegenerate}
                      disabled={isGenerating}
                    >
                      <RefreshCw className="h-4 w-4" />
                      Regenerate
                    </Button>
                  )}
                </div>
              )}
            </StepCard>
          </form>
        </FormProvider>

        {/* ── Step 4 / 5: Results ── */}
        {showTitles && titles.length > 0 && (
          <section className="relative flex flex-col gap-5 overflow-hidden rounded-xl border border-border bg-card p-4 sm:p-7">
            <div className="absolute left-0 right-0 top-0 h-px bg-gradient-to-r from-transparent via-primary/30 to-transparent" />
            <div>
              <div className="flex flex-wrap items-start justify-between gap-2">
                <h2 className="text-[18px] font-semibold tracking-tight text-foreground sm:text-[22px]">
                  Recommended titles
                </h2>
                <span className="hidden items-center gap-1.5 rounded-full bg-secondary px-3 py-1.5 text-xs font-medium text-muted-foreground sm:inline-flex">
                  Best match highlighted
                </span>
              </div>
              <p className="mt-1 text-sm text-muted-foreground">
                Ranked by hook strength, clarity, and YouTube-friendly phrasing.
              </p>
            </div>
            <TitleList
              titles={titles}
              onCopy={handleCopy}
              selectedTones={lastPayload?.tones || []}
            />
          </section>
        )}
      </div>
    </div>
  );
}
