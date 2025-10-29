'use client';

import { Dispatch, SetStateAction, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { InitialScriptWordCount } from 'defaultValues';
import { LinkIcon, MonitorPlayIcon, NewspaperIcon, Pencil, PlusIcon, X } from 'lucide-react';
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
import Button from 'components/ui/Button';
import Col from 'components/ui/Col';
import FormTextarea from 'components/ui/FormTextarea';
import H5 from 'components/ui/H5';
import Row from 'components/ui/Row';
import SuggestedTopicsPopover from 'components/ui/SuggestedTopicsPopover';
import Text from 'components/ui/Text';
import ExportIcon from 'components/icons/ExportIcon';
import FolderCloudIcon from 'components/icons/FolderCloudIcon';
import { Popover, PopoverContent, PopoverTrigger } from 'components/shadcn_ui/popover';

interface NicheDetailsType {
  id: number;
  title: string;
  tagline?: string;
  thumbnail_url?: string | null;
  script_structure?: {
    intro?: string;
    body?: string;
    conclusion?: string;
  };
  tone?: string[];
  pacing?: string[];
  top_channels?: { name: string; link: string }[];
  best_for?: string[];
}

export default function GenerateScriptForm({ configData }: { configData: GenerationPromptType }) {
  const toast = useToast();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [files, setFiles] = useState<Array<FileType>>([]);
  const { mutate: generateOutline, isPending } = useGenerateOutline();
  const [niche, setNiche] = useState<NicheDetailsType | null>(null);
  const nicheId = searchParams ? searchParams.get('nicheId') : null;

  useEffect(() => {
    if (!nicheId) return;

    const fetchNiche = async () => {
      try {
        const res = await getClientDataAction<{ data: NicheDetailsType }>(
          `auth/niches/${nicheId}/`,
        );
        setNiche(res.data);
        console.log('Fetched niche data:', res.data);
      } catch (err: any) {
        console.error('Error fetching niche details:', err?.response || err);
        setNiche(null);
      }
    };

    fetchNiche();
  }, [searchParams]);

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

  useEffect(() => {
    if (!niche) return;

    const availableTones = configData && Array.isArray(configData.tones) ? configData.tones : [];

    const preselectedToneIds: number[] = (niche.tone || [])
      .map((toneName) => {
        const found = availableTones.find(
          (t: any) => String(t.name).toLowerCase() === String(toneName).toLowerCase(),
        );
        return found ? Number(found.id) : null;
      })
      .filter((id): id is number => typeof id === 'number' && !Number.isNaN(id));

    if (preselectedToneIds.length > 0) {
      methods.setValue('tones', preselectedToneIds, { shouldDirty: true, shouldTouch: true });
      console.log('Prefilled tone IDs from niche:', preselectedToneIds);
    }
  }, [niche, configData, methods]);

  const { watch } = methods;

  const onSubmit = (_formData: FormType) => {
    const formValue = new FormData();
    const payload: Partial<FormType> = {};

    const normalizeTones = (tones: any): number[] => {
      if (!tones) return [];
      if (!Array.isArray(tones)) return [];
      return tones
        .map((t: any) => (typeof t === 'object' && t !== null ? Number(t.id) : Number(t)))
        .filter(Boolean);
    };

    const toneIds = normalizeTones(_formData.tones);

    if (!files.length) {
      payload.description = _formData.description;
      payload.tones = toneIds;
      if (_formData.template_style) {
        payload.template_style = _formData.template_style;
      } else {
        payload.min_length = _formData.min_length;
        payload.max_length = _formData.max_length;
      }
      payload.title = _formData.title;
      logger.info('Sending JSON payload:', payload);
    } else {
      formValue.append('description', _formData.description ?? '');
      toneIds.forEach((id) => formValue.append('tones', id.toString()));

      if (_formData.template_style) {
        formValue.append('template_style', _formData.template_style.toString());
      } else {
        formValue.append('min_length', String(_formData.min_length ?? 0));
        formValue.append('max_length', String(_formData.max_length ?? 500));
      }
      formValue.append('title', _formData.title ?? '');

      files.forEach((fileItem) => {
        if (fileItem.type === 'file' && fileItem.value instanceof File) {
          formValue.append('image', fileItem.value);
        } else if (fileItem.type === 'link' && typeof fileItem.value === 'string') {
          formValue.append('youtube_url', fileItem.value);
        } else if (fileItem.type === 'article' && typeof fileItem.value === 'string') {
          formValue.append('article_url', fileItem.value);
        }
      });

      logger.info('Sending FormData with files/links');
    }

    if (typeof window !== 'undefined') {
      try {
        const descToSave = files.length
          ? String(formValue.get('description') ?? '')
          : String(payload.description ?? '');
        console.log('descToSave', descToSave);
        localStorage.setItem('draft_description', descToSave);
      } catch (e) {
        logger.warn('Could not save draft_description to localStorage', e);
      }
    }

    generateOutline(files.length ? formValue : payload, {
      onSuccess: (data) => {
        logger.info('Outline generated:', data);
        toast.success('Success', 'Script outline generated successfully');
        router.push(`/new-script/${data.outline.uuid}`);
      },
      onError: (error) => {
        logger.error('Generate outline error:', error);
        toast.error('Something went wrong', 'Failed to generate script outline');
      },
    });
  };

  console.log('niche', niche);

  return (
    // eslint-disable-next-line react/jsx-props-no-spreading
    <FormProvider {...methods}>
      <form onSubmit={methods.handleSubmit(onSubmit)}>
        {isPending ? (
          <LoadingScreen />
        ) : (
          <Col className="gap-8">
            <div className="relative">
              <ContextButton files={files} setFiles={setFiles} />
              <FormTextarea
                name="description"
                validationSchema={{
                  required: 'Description is required',
                  minLength: { value: 50, message: 'Description must be at least 50 characters' },
                }}
                label={
                  <Row className="items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span> What&apos;s your video about?</span>
                      <InfoModal description="Be specific about your topic, audience, and key points you want to cover" />
                    </div>

                    {nicheId && (
                      <SuggestedTopicsPopover
                        suggestions={[
                          'Why people fake their own death',
                          'The man who disappeared... twice',
                          'A genius who changed the world, but no one knows their name',
                        ]}
                      />
                    )}
                  </Row>
                }
              />
            </div>
            <TemplatesWidget
              name="template_style"
              templates={configData.template_styles}
              // validationSchema={{
              //   required: 'Template style is required',
              // }}
            />
            <SliderWidget
              range={configData.length_range}
              defaultValue={InitialScriptWordCount}
              disabled={watch('template_style') !== undefined}
              validationSchema={{
                required: 'Length is required',
                min: { value: 500, message: 'Length must be at least 500 words' },
                validate: (_value: number, formValues: any) => {
                  if (
                    formValues &&
                    typeof formValues.min_length === 'number' &&
                    typeof formValues.max_length === 'number'
                  ) {
                    if (formValues.max_length - formValues.min_length < 500) {
                      return 'Difference between min_length and max_length must be at least 500 words';
                    }
                  }
                  return true;
                },
              }}
            />
            <VibeToneWidget tones={configData.tones} name="tones" />

            <Button disabled={isPending} type="submit">
              <Pencil size={16} /> Generate Script Outline
            </Button>
          </Col>
        )}
      </form>
    </FormProvider>
  );
}

type FileType = { type: 'link' | 'article' | 'file'; value: string | File };

function ContextButton({
  files,
  setFiles,
}: {
  files: FileType[];
  setFiles: Dispatch<SetStateAction<FileType[]>>;
}) {
  const toast = useToast();

  const [link, setLink] = useState<string>('');
  const [article, setArticle] = useState<string>('');
  const [file, setFile] = useState<File | null>(null);

  const handleFileUpload = (type: 'link' | 'article' | 'file', file: string | File) => {
    if (files.length >= 3) return toast.error('You can only add up to 3 files');
    setFiles([...files, { type, value: file }]);
    setLink('');
    setArticle('');
    setFile(null);
  };

  return (
    <div className="absolute bottom-3 right-3">
      <Popover>
        <PopoverTrigger asChild>
          <Button
            variant="gray"
            className="data-[state=open]:bg-white data-[state=open]:text-brand-surface"
          >
            <LinkIcon size={16} /> Add context {files.length > 0 ? '(' + files.length + ')' : ''}
          </Button>
        </PopoverTrigger>
        <PopoverContent
          side="top"
          align="end"
          className="w-full min-w-36 max-w-sm rounded-xl border border-[#BAFF38]/[12%] bg-[#484848] p-0"
        >
          <Col className="w-full gap-0">
            <Row className="w-full justify-normal border-b border-[#BAFF38]/[12%] p-3">
              <MonitorPlayIcon size={16} className="min-w-4 text-white" />
              <NewInput
                placeholder="Enter a YouTube video link"
                value={link}
                onChange={(e) => setLink(e.target.value)}
              />
              <NewButton onClick={() => link && handleFileUpload('link', link)} disabled={!link} />
            </Row>
            <Row className="w-full justify-normal border-b border-[#BAFF38]/[12%] p-3">
              <NewspaperIcon size={16} className="min-w-4 text-white" />
              <NewInput
                placeholder="Enter an article link"
                value={article}
                onChange={(e) => setArticle(e.target.value)}
              />
              <NewButton
                onClick={() => article && handleFileUpload('article', article)}
                disabled={!article}
              />
            </Row>
            <Row className="w-full justify-normal border-b border-[#BAFF38]/[12%] p-3">
              <FolderCloudIcon />
              <FileInput
                value={file}
                onChange={(e) => e.target.files && setFile(e.target.files?.[0])}
              />
              <NewButton
                isExport
                onClick={() => file && handleFileUpload('file', file)}
                disabled={!file}
              />
            </Row>
          </Col>

          <Col className="w-full gap-4 px-3 py-6">
            <Row>
              <H5>Attached links and files:</H5>
              <Text variant="xs" className="text-brand-secondary">
                Limit reached: {files.length} links
              </Text>
            </Row>
            {files.map((file, index) => (
              <Row key={index} className="w-full justify-normal text-white">
                {file.type === 'link' && <MonitorPlayIcon size={20} />}
                {file.type === 'article' && <NewspaperIcon size={20} />}
                {file.type === 'file' && <FolderCloudIcon />}
                <Text
                  variant="xs"
                  className="line-clamp-1 w-full max-w-[217px] overflow-hidden text-ellipsis"
                >
                  {file.value instanceof File ? file.value.name : file.value}
                </Text>
                <X size={20} onClick={() => setFiles(files.filter((_, i) => i !== index))} />
              </Row>
            ))}
          </Col>
        </PopoverContent>
      </Popover>
    </div>
  );
}

function NewButton({
  isExport,
  onClick,
  disabled,
}: {
  isExport?: boolean;
  onClick: () => void;
  disabled?: boolean;
}) {
  return (
    <button
      className="flex h-8 w-8 min-w-8 items-center justify-center rounded-full bg-[#2BFF13] opacity-60 disabled:bg-[#7C9971]"
      disabled={disabled}
      onClick={onClick}
    >
      {isExport ? <ExportIcon /> : <PlusIcon className="text-black" size={16} />}
    </button>
  );
}

function NewInput({
  placeholder,
  value,
  onChange,
}: {
  placeholder: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}) {
  return (
    <input
      type="text"
      placeholder={placeholder}
      className="w-ful h-8 w-[217px] rounded-xl border border-[#BAFF38]/[12%] bg-transparent p-4 text-xs text-white outline-0 placeholder:text-[#737373]"
      value={value}
      onChange={onChange}
    />
  );
}

function FileInput({
  value,
  onChange,
}: {
  value: File | null;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}) {
  return (
    <label className="flex h-10 w-[217px] cursor-pointer items-center rounded-2xl border border-[#BAFF38]/[12%] bg-[#484848] p-4 transition-colors hover:bg-[#5a5a5a]">
      <span className="flex-1 text-xs font-semibold text-[#E3E3E3]">Choose file</span>
      <span
        className="ml-auto max-w-[120px] truncate text-xs text-[#B0B0B0]"
        title={value?.name || 'No file chosen'}
      >
        {value?.name || 'No file chosen'}
      </span>
      <input
        type="file"
        className="hidden"
        accept="image/*"
        onChange={onChange}
        // value={value?.name || ''}
      />
    </label>
  );
}
