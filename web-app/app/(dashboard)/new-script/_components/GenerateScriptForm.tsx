'use client';

import { Dispatch, SetStateAction, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { InitialScriptWordCount } from 'defaultValues';
import { LinkIcon, MonitorPlayIcon, Paperclip, Pencil, PlusIcon, Upload, X } from 'lucide-react';
import { FormProvider, useForm } from 'react-hook-form';

import { FormType, GenerationPromptType } from '../types';
import { LoadingScreen } from './components';
import InfoModal from './InfoModal';
import SliderWidget from './SliderWidget';
import TemplatesWidget from './TemplatesWidget';
import VibeToneWidget from './VibeToneWidget';
import useGenerateOutline from 'lib/hooks/useGenerateOutline';
import { logger } from 'lib/logger';
import { getClientDataAction } from 'lib/utils/clientDataActions';
import useToast from 'lib/utils/useToast';
import { Button } from 'components/ui/Button';
import FormTextarea from 'components/ui/FormTextarea';
import { cn } from 'lib/utils';
import { Popover, PopoverContent, PopoverTrigger } from 'components/shadcn_ui/popover';

// ── Types ─────────────────────────────────────────────────────────────
type FileType = { type: 'link' | 'article' | 'file'; value: string | File };

interface NicheDetailsType {
  id: number;
  title: string;
  tagline?: string;
  thumbnail_url?: string | null;
  script_structure?: { intro?: string; body?: string; conclusion?: string };
  tone?: string[];
  pacing?: string[];
  top_channels?: { name: string; link: string }[];
  best_for?: string[];
}

// ── Main form ─────────────────────────────────────────────────────────
export default function GenerateScriptForm({ configData }: { configData: GenerationPromptType | null }) {
  const toast        = useToast();
  const router       = useRouter();
  const searchParams = useSearchParams();
  const [files, setFiles] = useState<FileType[]>([]);
  const { mutate: generateOutline, isPending } = useGenerateOutline();
  const [niche, setNiche] = useState<NicheDetailsType | null>(null);
  const nicheId = searchParams?.get('nicheId') ?? null;

  // ── Fetch niche if present ───────────────────────────────────────
  useEffect(() => {
    if (!nicheId) return;
    getClientDataAction<{ data: NicheDetailsType }>(`auth/niches/${nicheId}/`)
      .then((res) => setNiche(res.data))
      .catch(() => setNiche(null));
  }, [nicheId]);

  // ── Form setup ───────────────────────────────────────────────────
  const methods = useForm<FormType>({
    defaultValues: {
      description: '',
      tones: [],
      template_style: undefined,
      min_length: 0,
      max_length: 500,
      title: '',
    },
  });

  // Prefill tones from niche
  useEffect(() => {
    if (!niche) return;
    const availableTones = Array.isArray(configData?.tones) ? configData.tones : [];
    const preselected = (niche.tone ?? [])
      .map((name) => availableTones.find((t: any) => String(t.name).toLowerCase() === name.toLowerCase()))
      .filter(Boolean)
      .map((t: any) => Number(t.id))
      .filter((id) => Number.isFinite(id) && id !== 0);
    if (preselected.length > 0) {
      methods.setValue('tones', preselected, { shouldDirty: true, shouldTouch: true });
    }
  }, [niche, configData, methods]);

  // ── Helpers ──────────────────────────────────────────────────────
  const fileToDataUrl = (file: File): Promise<{ name: string; type: string; dataUrl: string }> =>
    new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload  = () => resolve({ name: file.name, type: file.type, dataUrl: String(reader.result) });
      reader.onerror = (e) => reject(e);
      reader.readAsDataURL(file);
    });

  const normalizeTones = (tones: any): number[] => {
    if (!tones || !Array.isArray(tones)) return [];
    return tones
      .map((t: any) => (typeof t === 'object' && t !== null ? Number(t.id) : Number(t)))
      .filter((n) => Number.isFinite(n) && n !== 0);
  };

  // ── Submit ───────────────────────────────────────────────────────
  const onSubmit = async (_formData: FormType) => {
    const formValue  = new FormData();
    const payload: Partial<FormType & { niche_id?: string }> = {};

    const toneIds      = normalizeTones(_formData.tones);
    const linkItems    = files.filter((f) => f.type === 'link'    && typeof f.value === 'string').map((f) => f.value as string);
    const articleItems = files.filter((f) => f.type === 'article' && typeof f.value === 'string').map((f) => f.value as string);
    const imageItems   = files.filter((f) => f.type === 'file'    && f.value instanceof File).map((f) => f.value as File);
    const hasImageFile = imageItems.some((file) => file?.size > 0);
    const nicheParam   = nicheId ?? undefined;

    if (!hasImageFile) {
      payload.description = _formData.description ?? '';
      payload.tones       = toneIds;
      if (_formData.template_style) payload.template_style = _formData.template_style;
      else { payload.min_length = _formData.min_length; payload.max_length = _formData.max_length; }
      payload.title = _formData.title ?? '';
      if (nicheParam) payload.niche_id = nicheParam;
      if (linkItems.length === 1)    payload.youtube_url = linkItems[0];
      else if (linkItems.length > 1) payload.youtube_url = linkItems;
      if (articleItems.length === 1)    payload.article_url = articleItems[0];
      else if (articleItems.length > 1) payload.article_url = articleItems;
    } else {
      formValue.append('description', _formData.description ?? '');
      toneIds.forEach((id) => formValue.append('tones', String(id)));
      if (_formData.template_style) formValue.append('template_style', String(_formData.template_style));
      else { formValue.append('min_length', String(_formData.min_length ?? 0)); formValue.append('max_length', String(_formData.max_length ?? 500)); }
      formValue.append('title', String(_formData.title ?? ''));
      if (nicheParam) formValue.append('niche_id', nicheParam);
      imageItems.forEach((file) => formValue.append('image', file));
      linkItems.forEach((l) => formValue.append('youtube_url', l));
      articleItems.forEach((a) => formValue.append('article_url', a));
    }

    // Persist to localStorage
    try {
      if (!hasImageFile) {
        localStorage.setItem('last_outline_payload', JSON.stringify({ hasImageFile: false, timestamp: Date.now(), payload }));
      } else {
        const imagesData = await Promise.all(imageItems.map(fileToDataUrl));
        localStorage.setItem('last_outline_payload', JSON.stringify({
          hasImageFile: true, timestamp: Date.now(),
          data: { description: _formData.description ?? '', tones: toneIds, template_style: _formData.template_style ?? null, min_length: _formData.min_length ?? 0, max_length: _formData.max_length ?? 500, title: _formData.title ?? '', niche_id: nicheParam ?? null, linkItems, articleItems, images: imagesData },
        }));
      }
      const descToSave = hasImageFile ? String(formValue.get('description') ?? '') : String(payload.description ?? '');
      localStorage.setItem('draft_description', descToSave);
    } catch (e) {
      logger.warn('Could not save to localStorage', e);
    }

    generateOutline(hasImageFile ? formValue : payload, {
      onSuccess: (data) => {
        toast.success('Success', 'Script outline generated successfully');
        router.push(`/new-script/${data.outline.uuid}`);
      },
      onError: (error) => {
        logger.error('Generate outline error:', error);
        toast.error('Something went wrong', 'Failed to generate script outline');
      },
    });
  };

  // ── Render ───────────────────────────────────────────────────────
  if (isPending) return <LoadingScreen />;

  return (
    <FormProvider {...methods}>
      <form onSubmit={methods.handleSubmit(onSubmit)} className="flex flex-col gap-6">

        {/* Niche badge */}
        {niche && (
          <div className="flex items-center gap-2 rounded-lg border border-border bg-accent px-3 py-2">
            <span className="text-xs text-muted-foreground">Niche template:</span>
            <span className="text-xs font-semibold text-accent-foreground">{niche.title}</span>
          </div>
        )}

        {/* Topic textarea */}
        <div className="relative">
          <FormTextarea
            name="description"
            validationSchema={{
              required: 'Description is required',
              minLength: { value: 50, message: 'Description must be at least 50 characters' },
            }}
            label={
              <div className="flex items-center gap-2">
                <span>What&apos;s your video about?</span>
                <InfoModal description="Be specific about your topic, audience, and key points you want to cover." />
              </div>
            }
            placeholder="e.g. Top 5 productivity hacks that actually work for creators who struggle with focus..."
            className="min-h-[140px] pb-12"
          />
          {/* Context button floated inside textarea */}
          <div className="absolute bottom-3 right-3">
            <ContextButton files={files} setFiles={setFiles} />
          </div>
        </div>

        {/* Attached files display */}
        {files.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {files.map((file, index) => (
              <div
                key={index}
                className="flex items-center gap-1.5 rounded-md border border-border bg-secondary px-2.5 py-1.5"
              >
                {file.type === 'link'    && <MonitorPlayIcon className="h-3.5 w-3.5 text-muted-foreground" />}
                {file.type === 'article' && <LinkIcon        className="h-3.5 w-3.5 text-muted-foreground" />}
                {file.type === 'file'    && <Paperclip       className="h-3.5 w-3.5 text-muted-foreground" />}
                <span className="max-w-[180px] truncate text-xs text-foreground">
                  {file.value instanceof File ? file.value.name : file.value}
                </span>
                <button
                  type="button"
                  onClick={() => setFiles(files.filter((_, i) => i !== index))}
                  className="ml-0.5 text-muted-foreground hover:text-foreground"
                >
                  <X className="h-3 w-3" />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Divider */}
        <div className="h-px bg-border" />

        {/* Template style */}
        <TemplatesWidget name="template_style" templates={configData?.template_styles ?? []} />

        {/* Script length */}
        <SliderWidget
          range={configData?.length_range ?? { min: 300, max: 3000, default: 1000 }}
          defaultValue={InitialScriptWordCount}
          disabled={methods.watch('template_style') !== undefined}
          validationSchema={{
            required: 'Length is required',
            min: { value: 500, message: 'Length must be at least 500 words' },
            validate: (_value: number, formValues: any) => {
              if (typeof formValues?.min_length === 'number' && typeof formValues?.max_length === 'number') {
                if (formValues.max_length - formValues.min_length < 500) {
                  return 'Difference between min and max must be at least 500 words';
                }
              }
              return true;
            },
          }}
        />

        {/* Tone */}
        <VibeToneWidget tones={configData?.tones ?? []} name="tones" />

        {/* Submit */}
        <Button type="submit" size="lg" loading={isPending} className="w-full">
          <Pencil className="h-4 w-4" />
          Generate Script Outline
        </Button>
      </form>
    </FormProvider>
  );
}

// ── Context button (add YouTube link / article / image) ───────────────
function ContextButton({
  files,
  setFiles,
}: {
  files: FileType[];
  setFiles: Dispatch<SetStateAction<FileType[]>>;
}) {
  const toast = useToast();
  const [link,    setLink]    = useState('');
  const [article, setArticle] = useState('');
  const [file,    setFile]    = useState<File | null>(null);

  const handleAdd = (type: 'link' | 'article' | 'file', value: string | File) => {
    if (files.length >= 3) return toast.error('You can only add up to 3 context items');
    setFiles([...files, { type, value }]);
    setLink(''); setArticle(''); setFile(null);
  };

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button
          type="button"
          variant="outline"
          size="sm"
          className={cn(files.length > 0 && 'border-primary/50 bg-accent text-accent-foreground')}
        >
          <Paperclip className="h-3.5 w-3.5" />
          Add context {files.length > 0 ? `(${files.length})` : ''}
        </Button>
      </PopoverTrigger>

      <PopoverContent
        side="top"
        align="end"
        className="w-80 rounded-xl border border-border bg-card p-0 shadow-md"
      >
        <div className="divide-y divide-border">
          {/* YouTube link */}
          <div className="flex items-center gap-2 p-3">
            <MonitorPlayIcon className="h-4 w-4 shrink-0 text-muted-foreground" />
            <input
              type="text"
              placeholder="YouTube video URL"
              value={link}
              onChange={(e) => setLink(e.target.value)}
              className="h-8 min-w-0 flex-1 rounded-md border border-border bg-input px-2 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
            />
            <button
              type="button"
              disabled={!link}
              onClick={() => link && handleAdd('link', link)}
              className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-primary text-primary-foreground disabled:opacity-40"
            >
              <PlusIcon className="h-3.5 w-3.5" />
            </button>
          </div>

          {/* Article link */}
          <div className="flex items-center gap-2 p-3">
            <LinkIcon className="h-4 w-4 shrink-0 text-muted-foreground" />
            <input
              type="text"
              placeholder="Article or blog URL"
              value={article}
              onChange={(e) => setArticle(e.target.value)}
              className="h-8 min-w-0 flex-1 rounded-md border border-border bg-input px-2 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
            />
            <button
              type="button"
              disabled={!article}
              onClick={() => article && handleAdd('article', article)}
              className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-primary text-primary-foreground disabled:opacity-40"
            >
              <PlusIcon className="h-3.5 w-3.5" />
            </button>
          </div>

          {/* Image upload */}
          <div className="flex items-center gap-2 p-3">
            <Upload className="h-4 w-4 shrink-0 text-muted-foreground" />
            <label className="flex h-8 min-w-0 flex-1 cursor-pointer items-center gap-1.5 rounded-md border border-border bg-input px-2 text-xs text-muted-foreground hover:bg-muted">
              {file ? (
                <span className="truncate text-foreground">{file.name}</span>
              ) : (
                'Upload image'
              )}
              <input
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(e) => e.target.files && setFile(e.target.files[0])}
              />
            </label>
            <button
              type="button"
              disabled={!file}
              onClick={() => file && handleAdd('file', file)}
              className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-primary text-primary-foreground disabled:opacity-40"
            >
              <PlusIcon className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>

        {files.length >= 3 && (
          <p className="px-3 py-2 text-xs text-muted-foreground">
            Maximum 3 context items reached.
          </p>
        )}
      </PopoverContent>
    </Popover>
  );
}
