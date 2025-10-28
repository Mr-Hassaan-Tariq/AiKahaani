'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Plus, Trash2 } from 'lucide-react';
import { Controller, FormProvider, useFieldArray, useForm } from 'react-hook-form';
import { toast } from 'sonner';

import NicheSelectWidget from './components/NicheSelectWidgets';
import {
  getClientDataAction,
  postClientDataAction,
  putClientDataAction,
} from 'lib/utils/clientDataActions';
import Button from 'components/ui/Button';
import Card from 'components/ui/Card';
import Input from 'components/ui/FormInput';
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
  thumbnailUrl?: string;
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
  const router = useRouter();
  const searchParams = useSearchParams();
  const nicheIdParam = searchParams?.get('nicheId') ?? undefined;
  const isEdit = Boolean(nicheIdParam);

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
      thumbnailUrl: undefined,
    },
  });

  const {
    control,
    handleSubmit,
    reset,
    setValue,
    formState: { errors, isSubmitting },
  } = methods;

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'channels',
  });

  const [isSubmittingLocal, setIsSubmittingLocal] = useState(false);

  // file selection (deferred upload)
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [thumbnailPreviewUrl, setThumbnailPreviewUrl] = useState<string | undefined>(undefined);
  const [uploadingThumbnail, setUploadingThumbnail] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    // cleanup preview URL when component unmounts or file changes
    return () => {
      if (thumbnailPreviewUrl) URL.revokeObjectURL(thumbnailPreviewUrl);
    };
  }, [thumbnailPreviewUrl]);

  const isYouTubeLink = (url: string) => {
    if (!url) return false;
    return YOUTUBE_URL_REGEX.test(url.trim());
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  // store selected file locally (no immediate upload)
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] ?? null;
    if (!file) {
      setSelectedFile(null);
      setThumbnailPreviewUrl(undefined);
      setValue('thumbnailUrl', undefined);
      return;
    }

    setSelectedFile(file);

    // generate preview
    const preview = URL.createObjectURL(file);
    // revoke previous preview
    if (thumbnailPreviewUrl) URL.revokeObjectURL(thumbnailPreviewUrl);
    setThumbnailPreviewUrl(preview);

    // keep form value in sync for possible usage
    setValue('thumbnailUrl', undefined); // will be set after upload
  };

  // Remove selected local file
  const handleRemoveSelectedFile = () => {
    setSelectedFile(null);
    if (thumbnailPreviewUrl) {
      URL.revokeObjectURL(thumbnailPreviewUrl);
    }
    setThumbnailPreviewUrl(undefined);
    setValue('thumbnailUrl', undefined);
    if (fileInputRef.current) fileInputRef.current.value = '';
    toast('Thumbnail removed');
  };

  // --- Fetch existing niche when editing and prefill the form ---
  const fetchAndPrefill = useCallback(
    async (id: string) => {
      try {
        const res = await getClientDataAction<{ data: any }>(`v1/admin/niches/${id}/`);
        const data = res?.data ?? res;
        if (!data) {
          toast.error('Failed to fetch niche for editing');
          return;
        }

        // Map server shape to form fields
        reset({
          title: data.title ?? '',
          description: data.tagline ?? '',
          tone: Array.isArray(data.tone) ? data.tone : (data.tone ?? []),
          pacing: Array.isArray(data.pacing) ? data.pacing : (data.pacing ?? []),
          channels:
            Array.isArray(data.top_channels) && data.top_channels.length > 0
              ? data.top_channels.map((c: any) => ({ name: c.name ?? '', link: c.link ?? '' }))
              : [{ name: '', link: '' }],
          bestFor: Array.isArray(data.best_for)
            ? (data.best_for as string[]).join(', ')
            : (data.best_for ?? []).join
              ? (data.best_for as string[]).join(', ')
              : '',
          structure: {
            intro: data.script_structure?.intro ?? '',
            body: data.script_structure?.body ?? '',
            outro: data.script_structure?.conclusion ?? '',
          },
          thumbnailUrl: data.thumbnail_url ?? undefined,
        });

        // show thumbnail preview if the server returned a thumbnail url
        if (data.thumbnail_url) {
          setThumbnailPreviewUrl(data.thumbnail_url);
        }
      } catch (err: any) {
        console.error('Error fetching niche for edit:', err);
        toast.error('Failed to load niche for editing');
      }
    },
    [reset],
  );

  useEffect(() => {
    if (isEdit && nicheIdParam) {
      fetchAndPrefill(nicheIdParam);
    }
  }, [isEdit, nicheIdParam, fetchAndPrefill]);

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

    try {
      let targetId: string | number | undefined = undefined;

      if (isEdit && nicheIdParam) {
        const putResp = await putClientDataAction<any, typeof payload>(
          `v1/admin/niches/${nicheIdParam}/`,
          payload,
        );

        toast.success('Niche updated successfully!');
      } else {
        const createResp = await postClientDataAction<any, typeof payload>(
          'v1/admin/niches/',
          payload,
        );
        targetId =
          createResp?.data?.id ?? createResp?.id ?? (createResp && (createResp as any).result?.id);
        if (!targetId) {
          console.warn('Create response did not include an id:', createResp);
        }
        toast.success('Niche created successfully!');
      }

      if (selectedFile && targetId) {
        setUploadingThumbnail(true);
        try {
          const formData = new FormData();
          formData.append('thumbnail', selectedFile);

          const uploadEndpoint = `v1/admin/niches/${targetId}/upload-thumbnail/`;
          const uploadResp = await postClientDataAction<
            { thumbnail_url: string; data: { thumbnail_url: string } },
            FormData
          >(uploadEndpoint, formData);

          const uploadedUrl = uploadResp?.data?.thumbnail_url ?? uploadResp?.thumbnail_url;
          if (uploadedUrl) {
            setValue('thumbnailUrl', uploadedUrl);
            toast.success('Thumbnail uploaded successfully!');
          } else {
            console.warn('Upload response missing thumbnail_url:', uploadResp);
            toast.error('Thumbnail uploaded but server did not return a URL.');
          }
        } catch (uploadErr) {
          console.error('Thumbnail upload failed:', uploadErr);
          toast.error('Thumbnail upload failed. Your niche was saved though.');
        } finally {
          setUploadingThumbnail(false);
        }
      }

      reset();
      router.push('/niches');
    } catch (err: any) {
      console.error('Error saving niche:', err);
      toast.error(err?.message ?? 'Failed to save niche');
    } finally {
      setIsSubmittingLocal(false);
    }
  };

  const FieldError = ({ message }: { message?: string }) => {
    if (!message) return null;
    return <p className="mt-1 text-xs text-rose-500">{message}</p>;
  };

  return (
    <main className="min-h-screen p-4 sm:p-6 lg:p-8">
      <Card className="mx-auto max-w-7xl border border-[#3C3C3C] bg-[#262724] p-6 lg:p-10">
        <h1 className="mb-2 text-3xl font-bold text-white">
          {isEdit ? 'Edit Niche' : 'Create New Niche'}
        </h1>
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
            <div className="md:col-span-2">
              <label className="mb-2 block text-sm font-medium text-white">Thumbnail</label>

              <div className="flex items-center gap-4">
                <div className="w-44">
                  {thumbnailPreviewUrl ? (
                    <img
                      src={thumbnailPreviewUrl}
                      alt="thumbnail preview"
                      className="h-28 w-full rounded-lg object-cover"
                    />
                  ) : (
                    <div className="flex h-28 w-full items-center justify-center rounded-lg bg-[#2a2a2a] text-sm text-gray-300">
                      No thumbnail selected
                    </div>
                  )}
                </div>

                <div className="flex flex-col gap-2">
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={handleFileChange}
                  />

                  <div className="flex gap-2">
                    <Button
                      type="button"
                      onClick={handleUploadClick}
                      disabled={uploadingThumbnail || isSubmittingLocal || isSubmitting}
                    >
                      {uploadingThumbnail
                        ? 'Uploading...'
                        : selectedFile
                          ? 'Change Thumbnail'
                          : 'Select Thumbnail'}
                    </Button>

                    {selectedFile && (
                      <button
                        type="button"
                        onClick={handleRemoveSelectedFile}
                        className="ml-2 inline-flex items-center gap-2 rounded-2xl border border-transparent bg-red-600 px-3 py-2 text-sm font-medium text-white hover:bg-red-700"
                      >
                        <Trash2 className="h-4 w-4" />
                        Remove
                      </button>
                    )}
                  </div>

                  <p className="text-xs text-gray-400">Recommended size: 1280x720. PNG or JPEG.</p>
                </div>
              </div>
            </div>

            {/* Title */}
            <Controller
              name="title"
              control={control}
              rules={{ required: 'Title is required' }}
              render={({ field }) => (
                <div>
                  <Input {...field} id="title" placeholder="Tech Reviews" label="Title" />
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
                </div>
              )}
            />

            <div></div>

            {/* Tone */}
            <Controller
              name="tone"
              control={control}
              rules={{
                validate: (val) =>
                  Array.isArray(val) && val.length > 0 ? true : 'Select at least one tone',
              }}
              render={({ field }) => (
                <NicheSelectWidget
                  options={toneOptions}
                  name={field.name}
                  label="Tone"
                  field={field}
                />
              )}
            />

            {/* Pacing */}
            <Controller
              name="pacing"
              control={control}
              rules={{
                validate: (val) =>
                  Array.isArray(val) && val.length > 0 ? true : 'Select at least one pacing style',
              }}
              render={({ field }) => (
                <NicheSelectWidget
                  options={pacingOptions}
                  name={field.name}
                  label="Pacing"
                  field={field}
                />
              )}
            />

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

            <div className="flex w-full justify-center pt-4 md:col-span-2">
              <div className="w-full max-w-md">
                <Button
                  type="submit"
                  variant="green"
                  className="w-full"
                  disabled={isSubmitting || isSubmittingLocal || uploadingThumbnail}
                >
                  {isSubmitting || isSubmittingLocal || uploadingThumbnail
                    ? isEdit
                      ? 'Updating...'
                      : 'Creating...'
                    : isEdit
                      ? 'Update Niche'
                      : 'Create Niche'}
                </Button>
              </div>
            </div>
          </form>
        </FormProvider>
      </Card>
    </main>
  );
}
