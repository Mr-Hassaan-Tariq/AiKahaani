'use client';

import { useState } from 'react';
import { LinkIcon, MonitorPlayIcon, NewspaperIcon, Pencil, PlusIcon, X } from 'lucide-react';

import { LoadingScreen } from './components';
import InfoModal from './InfoModal';
import SliderWidget from './SliderWidget';
import TemplatesWidget from './TemplatesWidget';
import VibeToneWidget from './VibeToneWidget';
import useToast from 'lib/utils/useToast';
import Button from 'components/ui/Button';
import Col from 'components/ui/Col';
import FormTextarea from 'components/ui/FormTextarea';
import H5 from 'components/ui/H5';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';
import ExportIcon from 'components/icons/ExportIcon';
import FolderCloudIcon from 'components/icons/FolderCloudIcon';
import { Popover, PopoverContent, PopoverTrigger } from 'components/shadcn_ui/popover';

export default function GenerateScriptForm() {
  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerateScript = () => {
    setIsGenerating(true);
    // Simulate API call - replace with actual implementation
    setTimeout(() => {
      setIsGenerating(false);
    }, 5000);
  };

  return isGenerating ? (
    <LoadingScreen />
  ) : (
    <Col className="gap-8">
      <div className="relative">
        <ContextButton />
        <FormTextarea
          label={
            <Row className="justify-normal gap-2">
              <span> What&apos;s your video about?</span>
              <InfoModal description="Be specific about your topic, audience, and key points you want to cover" />
            </Row>
          }
        />
      </div>
      <TemplatesWidget />
      <SliderWidget />
      <VibeToneWidget />

      <Button disabled={isGenerating} onClick={handleGenerateScript}>
        <Pencil size={16} /> Generate Script Outline
      </Button>
    </Col>
  );
}

type FileType = { type: 'link' | 'article' | 'file'; value: string | File };

function ContextButton() {
  const toast = useToast();
  const [files, setFiles] = useState<Array<FileType>>([]);
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
        accept=".pdf,.doc,.docx,.txt,video/*"
        className="hidden"
        onChange={onChange}
        // value={value?.name || ''}
      />
    </label>
  );
}
