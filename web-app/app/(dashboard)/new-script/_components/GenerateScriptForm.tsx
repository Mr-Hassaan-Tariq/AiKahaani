'use client';

import { Dispatch, SetStateAction, useEffect, useRef, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import {
  Film,
  Layers,
  LinkIcon,
  ListTree,
  MonitorPlayIcon,
  Paperclip,
  Plus,
  PlusIcon,
  SlidersHorizontal,
  Sparkles,
  Upload,
  Wand2,
  X,
  Zap,
} from 'lucide-react';
import { FormProvider, useForm } from 'react-hook-form';

import { FormType, GenerationPromptType, ToneType } from '../types';
import { LoadingScreen } from './components';
import useGenerateOutline from 'lib/hooks/useGenerateOutline';
import { logger } from 'lib/logger';
import { cn } from 'lib/utils';
import { getClientDataAction } from 'lib/utils/clientDataActions';
import useToast from 'lib/utils/useToast';
import { Button } from 'components/ui/Button';
import { Popover, PopoverContent, PopoverTrigger } from 'components/shadcn_ui/popover';

// ── Types ─────────────────────────────────────────────────────────────
type FileType = { type: 'link' | 'article' | 'file'; value: string | File };

interface NicheDetailsType {
  id: number;
  title: string;
  tagline?: string;
  thumbnail_url?: string | null;
  tone?: string[];
}

// ── Icon map for template styles ──────────────────────────────────────
const templateIcons: Record<string, React.ElementType> = {
  'Short-form': Zap,
  Standard: Layers,
  'Long-form': Film,
  Outline: ListTree,
};

function getTemplateIcon(name: string) {
  for (const [key, Icon] of Object.entries(templateIcons)) {
    if (name.toLowerCase().includes(key.toLowerCase())) return Icon;
  }
  return Layers;
}

// ── Main form ─────────────────────────────────────────────────────────
export default function GenerateScriptForm({
  configData,
}: {
  configData: GenerationPromptType | null;
}) {
  const toast = useToast();
  const router = useRouter();
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
      max_length: 1500,
      title: '',
    },
  });

  const { watch, setValue, register } = methods;
  const selectedTemplateId = watch('template_style');
  const selectedToneIds = watch('tones') as number[];
  const maxLength = watch('max_length') as number;

  // Prefill tones from niche
  useEffect(() => {
    if (!niche) return;
    const available = Array.isArray(configData?.tones) ? configData.tones : [];
    const preselected = (niche.tone ?? [])
      .map((name) =>
        available.find((t: any) => String(t.name).toLowerCase() === name.toLowerCase()),
      )
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
      reader.onload = () =>
        resolve({ name: file.name, type: file.type, dataUrl: String(reader.result) });
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
    const formValue = new FormData();
    const payload: Partial<FormType & { niche_id?: string }> = {};

    const toneIds = normalizeTones(_formData.tones);
    const linkItems = files
      .filter((f) => f.type === 'link' && typeof f.value === 'string')
      .map((f) => f.value as string);
    const articleItems = files
      .filter((f) => f.type === 'article' && typeof f.value === 'string')
      .map((f) => f.value as string);
    const imageItems = files
      .filter((f) => f.type === 'file' && f.value instanceof File)
      .map((f) => f.value as File);
    const hasImageFile = imageItems.some((file) => file?.size > 0);
    const nicheParam = nicheId ?? undefined;

    if (!hasImageFile) {
      payload.description = _formData.description ?? '';
      payload.tones = toneIds;
      if (_formData.template_style) payload.template_style = _formData.template_style;
      else {
        payload.min_length = _formData.min_length;
        payload.max_length = _formData.max_length;
      }
      payload.title = _formData.title ?? '';
      if (nicheParam) payload.niche_id = nicheParam;
      if (linkItems.length === 1) payload.youtube_url = linkItems[0];
      else if (linkItems.length > 1) payload.youtube_url = linkItems;
      if (articleItems.length === 1) payload.article_url = articleItems[0];
      else if (articleItems.length > 1) payload.article_url = articleItems;
    } else {
      formValue.append('description', _formData.description ?? '');
      toneIds.forEach((id) => formValue.append('tones', String(id)));
      if (_formData.template_style)
        formValue.append('template_style', String(_formData.template_style));
      else {
        formValue.append('min_length', String(_formData.min_length ?? 0));
        formValue.append('max_length', String(_formData.max_length ?? 500));
      }
      formValue.append('title', String(_formData.title ?? ''));
      if (nicheParam) formValue.append('niche_id', nicheParam);
      imageItems.forEach((file) => formValue.append('image', file));
      linkItems.forEach((l) => formValue.append('youtube_url', l));
      articleItems.forEach((a) => formValue.append('article_url', a));
    }

    try {
      if (!hasImageFile) {
        localStorage.setItem(
          'last_outline_payload',
          JSON.stringify({ hasImageFile: false, timestamp: Date.now(), payload }),
        );
      } else {
        const imagesData = await Promise.all(imageItems.map(fileToDataUrl));
        localStorage.setItem(
          'last_outline_payload',
          JSON.stringify({
            hasImageFile: true,
            timestamp: Date.now(),
            data: {
              description: _formData.description ?? '',
              tones: toneIds,
              template_style: _formData.template_style ?? null,
              min_length: _formData.min_length ?? 0,
              max_length: _formData.max_length ?? 500,
              title: _formData.title ?? '',
              niche_id: nicheParam ?? null,
              linkItems,
              articleItems,
              images: imagesData,
            },
          }),
        );
      }
      const descToSave = hasImageFile
        ? String(formValue.get('description') ?? '')
        : String(payload.description ?? '');
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

  if (isPending) return <LoadingScreen />;

  const templates = configData?.template_styles ?? [];
  const allTones = configData?.tones ?? [];
  const range = configData?.length_range ?? { min: 300, max: 3000, default: 1000 };

  // Tones helpers
  const toggleTone = (id: number) => {
    const current = (methods.getValues('tones') as number[]) ?? [];
    if (current.includes(id)) {
      setValue(
        'tones',
        current.filter((t) => t !== id),
      );
    } else if (current.length < 3) {
      setValue('tones', [...current, id]);
    }
  };

  return (
    <FormProvider {...methods}>
      <form onSubmit={methods.handleSubmit(onSubmit)} className="flex flex-1 flex-col overflow-y-auto sm:flex-row sm:overflow-hidden">
        {/* ═══ LEFT: Editor pane ═══════════════════════════════════════ */}
        <div className="flex min-w-0 flex-1 flex-col gap-6 px-4 py-6 sm:gap-8 sm:overflow-y-auto sm:px-10 sm:py-10">
          {/* Niche badge */}
          {niche && (
            <div className="flex items-center gap-2 self-start rounded-lg border border-border bg-accent px-3 py-2">
              <span className="text-xs text-muted-foreground">Niche template:</span>
              <span className="text-xs font-semibold text-accent-foreground">{niche.title}</span>
            </div>
          )}

          {/* Title input */}
          <input
            {...register('title')}
            placeholder="Give your script a working title…"
            className="w-full border-none bg-transparent text-[22px] font-bold leading-tight tracking-tight text-foreground outline-none placeholder:text-muted-foreground/40 sm:text-[32px]"
          />

          {/* Prompt section */}
          <div className="flex flex-col gap-3">
            <label className="flex items-center gap-2 text-sm font-semibold text-primary">
              <Sparkles className="h-4 w-4" />
              Describe the video you want to turn into a script
            </label>

            <div className="rounded-lg border border-border bg-secondary p-6">
              <textarea
                {...register('description', {
                  required: 'Description is required',
                  minLength: { value: 50, message: 'Description must be at least 50 characters' },
                })}
                placeholder="Create a high-retention YouTube script for creators who want to grow with educational content. Start with a curiosity-driven hook, explain 5 practical scripting methods, add pattern interrupts, and finish with a strong subscribe CTA."
                rows={8}
                className="w-full resize-none bg-transparent text-base leading-relaxed text-foreground outline-none placeholder:text-muted-foreground"
              />

              {/* Textarea footer */}
              <div className="mt-4 flex items-center justify-between gap-3 border-t border-border pt-4">
                <div className="flex items-center gap-1.5">
                  <ContextButton files={files} setFiles={setFiles} />
                </div>
                <span className="text-xs text-muted-foreground">
                  Add notes, links, or research points
                </span>
              </div>
            </div>

            {/* Description error */}
            {methods.formState.errors.description && (
              <p className="text-xs text-destructive">
                {methods.formState.errors.description.message}
              </p>
            )}
          </div>

          {/* Attached files */}
          {files.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {files.map((file, index) => (
                <div
                  key={index}
                  className="flex items-center gap-1.5 rounded-md border border-border bg-card px-2.5 py-1.5"
                >
                  {file.type === 'link' && (
                    <MonitorPlayIcon className="h-3.5 w-3.5 text-muted-foreground" />
                  )}
                  {file.type === 'article' && (
                    <LinkIcon className="h-3.5 w-3.5 text-muted-foreground" />
                  )}
                  {file.type === 'file' && (
                    <Paperclip className="h-3.5 w-3.5 text-muted-foreground" />
                  )}
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
        </div>

        {/* ═══ RIGHT: Inspector pane ═══════════════════════════════════ */}
        <div className="flex shrink-0 flex-col border-t border-border bg-card sm:w-[440px] sm:overflow-hidden sm:border-l sm:border-t-0">
          {/* Inspector header */}
          <div className="flex items-center gap-2 border-b border-border px-5 py-4 sm:px-7 sm:py-5">
            <SlidersHorizontal className="h-4 w-4 text-muted-foreground" />
            <span className="text-[15px] font-semibold text-foreground">Script Settings</span>
          </div>

          {/* Inspector body — scrollable */}
          <div className="flex flex-1 flex-col gap-6 px-5 py-5 sm:gap-8 sm:overflow-y-auto sm:px-7 sm:py-6">
            {/* ── Output Format ── */}
            <div className="flex flex-col gap-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-semibold text-foreground">Output format</span>
                <span className="text-xs text-muted-foreground">Choose one</span>
              </div>
              <div className="grid grid-cols-2 gap-3">
                {templates.map((tmpl) => {
                  const Icon = getTemplateIcon(tmpl.name);
                  const isSelected = selectedTemplateId === tmpl.id;
                  return (
                    <button
                      key={tmpl.id}
                      type="button"
                      onClick={() => setValue('template_style', isSelected ? undefined : tmpl.id)}
                      className={cn(
                        'flex flex-col gap-2 rounded-lg border p-3 text-left transition-colors',
                        isSelected
                          ? 'border-primary bg-accent'
                          : 'border-border bg-background hover:bg-secondary',
                      )}
                    >
                      <div
                        className={cn(
                          'flex h-8 w-8 items-center justify-center rounded-md',
                          isSelected ? 'bg-primary' : 'bg-muted',
                        )}
                      >
                        <Icon
                          className={cn(
                            'h-4 w-4',
                            isSelected ? 'text-primary-foreground' : 'text-muted-foreground',
                          )}
                        />
                      </div>
                      <p className="text-[13px] font-semibold leading-tight text-foreground">
                        {tmpl.name}
                      </p>
                      <p className="text-[11px] leading-tight text-muted-foreground">
                        {tmpl.description}
                      </p>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* ── Script Length ── */}
            <div className="flex flex-col gap-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-semibold text-foreground">Script length</span>
                <span className="text-xs text-muted-foreground">
                  ~{(maxLength || range.default).toLocaleString()} words
                </span>
              </div>
              <LengthSlider
                range={range}
                disabled={selectedTemplateId !== undefined}
                value={maxLength || range.default}
                onChange={(val) => {
                  const half = Math.round((val - range.min) * 0.4);
                  setValue('min_length', range.min + half);
                  setValue('max_length', val);
                }}
              />
              <div className="flex justify-between text-[11px] text-muted-foreground">
                <span>Short</span>
                <span>Long form</span>
              </div>
              {selectedTemplateId !== undefined && (
                <p className="text-[11px] text-muted-foreground">Length set by selected format.</p>
              )}
            </div>

            {/* ── Creator Voice ── */}
            <div className="flex flex-col gap-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-semibold text-foreground">Creator voice</span>
                <span className="text-xs text-muted-foreground">Up to 3 styles</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {/* Selected tone chips */}
                {selectedToneIds.map((id) => {
                  const tone = allTones.find((t: ToneType) => t.id === id);
                  if (!tone) return null;
                  return (
                    <span
                      key={id}
                      className="flex items-center gap-1.5 rounded-full border border-border bg-secondary px-3 py-1 text-xs font-medium text-foreground"
                    >
                      {tone.name}
                      <button
                        type="button"
                        onClick={() => toggleTone(id)}
                        className="text-muted-foreground hover:text-foreground"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </span>
                  );
                })}

                {/* Add style popover */}
                {selectedToneIds.length < 3 && (
                  <AddTonePopover
                    allTones={allTones}
                    selectedIds={selectedToneIds}
                    onToggle={toggleTone}
                  />
                )}
              </div>
            </div>
          </div>

          {/* Inspector footer — Generate button */}
          <div className="shrink-0 border-t border-border px-5 py-4 sm:px-7 sm:py-5">
            <Button
              type="submit"
              loading={isPending}
              className="h-12 w-full text-[15px] font-semibold shadow-[0_8px_16px_rgba(255,0,0,0.15)]"
            >
              <Wand2 className="h-[18px] w-[18px]" />
              Generate YouTube Script
            </Button>
          </div>
        </div>
      </form>
    </FormProvider>
  );
}

// ── Length slider ─────────────────────────────────────────────────────
function LengthSlider({
  range,
  value,
  onChange,
  disabled,
}: {
  range: { min: number; max: number };
  value: number;
  onChange: (val: number) => void;
  disabled?: boolean;
}) {
  const pct = Math.round(((value - range.min) / (range.max - range.min)) * 100);
  return (
    <div className="relative flex items-center">
      <input
        type="range"
        min={range.min}
        max={range.max}
        step={100}
        value={value}
        disabled={disabled}
        onChange={(e) => onChange(Number(e.target.value))}
        className="h-1.5 w-full cursor-pointer appearance-none rounded-full bg-secondary disabled:cursor-not-allowed disabled:opacity-50"
        style={{
          background: disabled
            ? undefined
            : `linear-gradient(to right, hsl(var(--primary)) ${pct}%, hsl(var(--secondary)) ${pct}%)`,
        }}
      />
    </div>
  );
}

// ── Add tone popover ──────────────────────────────────────────────────
function AddTonePopover({
  allTones,
  selectedIds,
  onToggle,
}: {
  allTones: ToneType[];
  selectedIds: number[];
  onToggle: (id: number) => void;
}) {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <button
          type="button"
          className="flex items-center gap-1 rounded-full border border-dashed border-border px-3 py-1 text-xs font-medium text-muted-foreground transition-colors hover:border-primary hover:text-primary"
        >
          <Plus className="h-3 w-3" />
          Add style
        </button>
      </PopoverTrigger>
      <PopoverContent side="top" align="start" className="w-52 p-2">
        <div className="flex flex-col gap-0.5">
          {allTones
            .filter((t) => !selectedIds.includes(t.id))
            .map((tone) => (
              <button
                key={tone.id}
                type="button"
                onClick={() => onToggle(tone.id)}
                className="flex items-center gap-2 rounded-md px-3 py-2 text-left text-sm text-foreground hover:bg-secondary"
              >
                {tone.name}
              </button>
            ))}
          {allTones.filter((t) => !selectedIds.includes(t.id)).length === 0 && (
            <p className="px-3 py-2 text-xs text-muted-foreground">All styles selected</p>
          )}
        </div>
      </PopoverContent>
    </Popover>
  );
}

// ── Context button (attach YouTube / article / image) ─────────────────
function ContextButton({
  files,
  setFiles,
}: {
  files: FileType[];
  setFiles: Dispatch<SetStateAction<FileType[]>>;
}) {
  const toast = useToast();
  const [link, setLink] = useState('');
  const [article, setArticle] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleAdd = (type: 'link' | 'article' | 'file', value: string | File) => {
    if (files.length >= 3) return toast.error('You can only add up to 3 context items');
    setFiles([...files, { type, value }]);
    setLink('');
    setArticle('');
    setFile(null);
  };

  return (
    <Popover>
      <PopoverTrigger asChild>
        <button
          type="button"
          className={cn(
            'flex h-8 w-8 items-center justify-center rounded-md border border-border text-muted-foreground transition-colors hover:bg-muted hover:text-foreground',
            files.some((f) => f.type === 'file') && 'border-primary/50 text-primary',
          )}
        >
          <Paperclip className="h-4 w-4" />
        </button>
      </PopoverTrigger>

      <PopoverContent
        side="top"
        align="start"
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
                ref={fileInputRef}
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
