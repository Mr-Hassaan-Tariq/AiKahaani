'use client';

import { useState } from 'react';
import { Plus, Trash2 } from 'lucide-react';
import { Controller, FormProvider, useFieldArray, useForm } from 'react-hook-form';
import Select from 'react-select';
import { toast } from 'sonner';

import { postClientDataAction } from 'lib/utils/clientDataActions';
import Button from 'components/ui/Button';
import Card from 'components/ui/Card';
import Input from 'components/ui/FormInput';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';

type Channel = {
  name: string;
  link: string;
};

type CardData = {
  title: string;
  description: string;
  tone: string[];
  pacing: string[];
  channels: Channel[];
  bestFor: string;
  structure: {
    intro: string;
    body: string;
    outro: string;
  };
};

const toneOptions = [
  { value: 'Neutral', label: 'Neutral' },
  { value: 'Educational', label: 'Educational' },
  { value: 'Professional', label: 'Professional' },
  { value: 'Engaging', label: 'Engaging' },
  { value: 'Conversational', label: 'Conversational' },
  { value: 'Storytelling', label: 'Storytelling' },
];

const pacingOptions = [
  { value: 'Fast', label: 'Fast' },
  { value: 'Dynamic', label: 'Dynamic' },
  { value: 'Moderate', label: 'Moderate' },
  { value: 'Slow', label: 'Slow' },
];

const YOUTUBE_URL_REGEX = /^https?:\/\/(?:www\.)?(?:youtube\.com\/.+|youtu\.be\/.+)$/i;

export default function CreateNicheModal() {
  const methods = useForm<CardData>({
    mode: 'onBlur',
    defaultValues: {
      title: '',
      description: '',
      tone: [],
      pacing: [],
      channels: [{ name: '', link: '' }],
      bestFor: '',
      structure: {
        intro: '',
        body: '',
        outro: '',
      },
    },
  });

  const {
    control,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = methods;

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'channels',
  });

  const [isSubmittingLocal, setIsSubmittingLocal] = useState(false);

  const isYouTubeLink = (url: string) => {
    if (!url) return false;
    return YOUTUBE_URL_REGEX.test(url.trim());
  };

  const onSubmit = async (data: CardData) => {
    setIsSubmittingLocal(true);
    const payload = {
      title: data.title,
      tagline: data.description,
      tone: data.tone,
      pacing: data.pacing,
      top_channels: data.channels.filter((ch) => ch.name && ch.link),
      best_for: data.bestFor ? data.bestFor.split(',').map((s) => s.trim()) : [],
      script_structure: {
        intro: data.structure.intro,
        body: data.structure.body,
        conclusion: data.structure.outro,
      },
      status: 'active',
    };

    console.log('Sending Payload:', payload);

    try {
      const response = await postClientDataAction<any, typeof payload>('v1/admin/niches/', payload);

      toast.success('Niche created successfully!');
      reset();
    } catch (error: any) {
      console.error('Error creating niche:', error);
      toast.error('Failed to create niche. Please try again.');
    } finally {
      setIsSubmittingLocal(false);
    }
  };

  const customSelectStyles = {
    control: (base: any) => ({
      ...base,
      backgroundColor: 'rgba(255,255,255,0.03)',
      border: 'none',
      borderRadius: '0.6rem',
      padding: '2px 4px',
      boxShadow: 'none',
    }),
    menu: (base: any) => ({
      ...base,
      backgroundColor: '#f9fafb',
      borderRadius: '0.5rem',
    }),
    option: (base: any, state: { isFocused: boolean }) => ({
      ...base,
      backgroundColor: state.isFocused ? '#e5e7eb' : '#f9fafb',
      color: '#000',
    }),
  };

  const FieldError = ({ message }: { message?: string }) => {
    if (!message) return null;
    return <p className="mt-1 text-xs text-rose-500">{message}</p>;
  };

  return (
    <main className="min-h-screen p-4 sm:p-6 lg:p-8">
      <Card className="mx-auto max-w-4xl border border-[#3C3C3C] bg-[#262724] p-6 lg:p-10">
        <h1 className="mb-2 text-3xl font-bold text-white">Create New Niche</h1>
        <Text className="mb-8 text-[#AAACA6]">
          Define the style, tone, and competitive channels for your new YouTube niche.
        </Text>

        <FormProvider {...methods}>
          <form
            id="createNicheForm"
            onSubmit={handleSubmit(onSubmit)}
            className="grid gap-6 py-5 md:grid-cols-2"
            noValidate
          >
            {/* Title */}
            <Controller
              name="title"
              control={control}
              rules={{ required: 'Title is required' }}
              render={({ field }) => (
                <div>
                  <Input {...field} id="title" placeholder="Tech Reviews" label="Title" />
                  {/* <FieldError message={errors?.title?.message as string | undefined} /> */}
                </div>
              )}
            />

            {/* Description */}
            <Controller
              name="description"
              control={control}
              rules={{ required: 'Description is required' }}
              render={({ field }) => (
                <div>
                  <Input
                    {...field}
                    id="description"
                    type="textarea"
                    placeholder="Latest tech product reviews and analysis"
                    label="Tagline / Description"
                  />
                  {/* <FieldError message={errors?.description?.message as string | undefined} /> */}
                </div>
              )}
            />

            {/* Script Structure */}
            <div className="md:col-span-2">
              <Text variant="base" className="mb-2 font-medium text-white">
                Script Structure
              </Text>

              <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
                <Controller
                  name="structure.intro"
                  control={control}
                  rules={{ required: 'Intro is required' }}
                  render={({ field }) => (
                    <div>
                      <Input {...field} label="Intro" placeholder="Hook with latest tech trend" />
                      <FieldError
                        message={(errors?.structure as any)?.intro?.message as string | undefined}
                      />
                    </div>
                  )}
                />

                <Controller
                  name="structure.body"
                  control={control}
                  rules={{ required: 'Body is required' }}
                  render={({ field }) => (
                    <div>
                      <Input {...field} label="Body" placeholder="Detailed review" />
                      <FieldError
                        message={(errors?.structure as any)?.body?.message as string | undefined}
                      />
                    </div>
                  )}
                />

                <Controller
                  name="structure.outro"
                  control={control}
                  rules={{ required: 'Conclusion is required' }}
                  render={({ field }) => (
                    <div>
                      <Input {...field} label="Conclusion" placeholder="Recommendation" />
                      <FieldError
                        message={(errors?.structure as any)?.outro?.message as string | undefined}
                      />
                    </div>
                  )}
                />
              </div>
            </div>

            {/* Best For */}
            <Controller
              name="bestFor"
              control={control}
              rules={{ required: 'Best For is required' }}
              render={({ field }) => (
                <div>
                  <Input
                    {...field}
                    id="bestFor"
                    placeholder="Technology, Product Reviews, Gadgets"
                    label="Best For (comma separated)"
                  />
                  {/* <FieldError message={errors?.bestFor?.message as string | undefined} /> */}
                </div>
              )}
            />

            <div></div>

            {/* Tone */}
            <div className="flex flex-col gap-2">
              <Text variant="base" className="font-medium text-white">
                Tone
              </Text>
              <Controller
                name="tone"
                control={control}
                rules={{
                  validate: (val) =>
                    Array.isArray(val) && val.length > 0 ? true : 'Select at least one tone',
                }}
                render={({ field }) => (
                  <div>
                    <Select
                      {...field}
                      isMulti
                      options={toneOptions}
                      placeholder="Select tone(s)"
                      onChange={(selected) => field.onChange(selected?.map((s) => s.value) || [])}
                      onBlur={field.onBlur}
                      value={toneOptions.filter((opt) => field.value.includes(opt.value))}
                      styles={customSelectStyles}
                    />
                    <FieldError message={errors?.tone?.message as string | undefined} />
                  </div>
                )}
              />
            </div>

            {/* Pacing */}
            <div className="flex flex-col gap-2">
              <Text variant="base" className="font-medium text-white">
                Pacing
              </Text>
              <Controller
                name="pacing"
                control={control}
                rules={{
                  validate: (val) =>
                    Array.isArray(val) && val.length > 0
                      ? true
                      : 'Select at least one pacing style',
                }}
                render={({ field }) => (
                  <div>
                    <Select
                      {...field}
                      isMulti
                      options={pacingOptions}
                      placeholder="Select pacing style(s)"
                      onChange={(selected) => field.onChange(selected?.map((s) => s.value) || [])}
                      onBlur={field.onBlur}
                      value={pacingOptions.filter((opt) => field.value.includes(opt.value))}
                      styles={customSelectStyles}
                    />
                    <FieldError message={errors?.pacing?.message as string | undefined} />
                  </div>
                )}
              />
            </div>

            {/* Channels */}
            <div className="md:col-span-2">
              <div className="mb-2 flex items-center justify-between">
                <Text className="text-base font-semibold text-white">Top Channels</Text>
                <button
                  type="button"
                  onClick={() => append({ name: '', link: '' })}
                  className="flex items-center gap-1 text-sm text-green-500"
                >
                  <Plus className="h-4 w-4" /> Add Channel
                </button>
              </div>

              {fields.map((f, index) => {
                const channelErrors = (errors?.channels as any)?.[index] as
                  | { name?: { message?: string }; link?: { message?: string } }
                  | undefined;

                return (
                  <div
                    key={f.id}
                    className="mb-3 grid grid-cols-1 items-center gap-4 md:grid-cols-[1fr_1fr_auto]"
                  >
                    <Controller
                      name={`channels.${index}.name`}
                      control={control}
                      rules={{ required: 'Channel name is required' }}
                      render={({ field }) => (
                        <div>
                          <Input {...field} label="Channel Name" placeholder="MKBHD" />
                          <FieldError message={channelErrors?.name?.message} />
                        </div>
                      )}
                    />

                    <Controller
                      name={`channels.${index}.link`}
                      control={control}
                      rules={{
                        required: 'Channel link is required',
                        validate: (val) =>
                          typeof val === 'string' && val.trim().length > 0
                            ? YOUTUBE_URL_REGEX.test(val.trim()) ||
                              'Please enter a valid YouTube URL (youtube.com or youtu.be)'
                            : 'Channel link is required',
                      }}
                      render={({ field }) => {
                        const value = field.value ?? '';
                        const validYouTube = typeof value === 'string' && isYouTubeLink(value);
                        return (
                          <div>
                            <Input
                              {...field}
                              label="Channel Link"
                              placeholder="https://youtube.com/@mkbhd"
                            />
                            <FieldError message={channelErrors?.link?.message} />

                            {validYouTube && value.trim().toLowerCase().startsWith('http') && (
                              <div className="mt-1">
                                <a
                                  href={value}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-sm text-blue-400 underline"
                                >
                                  Open Link
                                </a>
                              </div>
                            )}
                          </div>
                        );
                      }}
                    />

                    <div className="mt-7 flex items-center justify-center">
                      <button
                        type="button"
                        onClick={() => remove(index)}
                        className="text-red-500 hover:text-red-700"
                        aria-label={`Remove channel ${index + 1}`}
                      >
                        <Trash2 className="h-5 w-5" />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>

            <Row className="w-full pt-4">
              <Button type="submit" variant="green" disabled={isSubmitting || isSubmittingLocal}>
                {isSubmitting || isSubmittingLocal ? 'Creating...' : 'Create Niche'}
              </Button>
            </Row>
          </form>
        </FormProvider>
      </Card>
    </main>
  );
}
