'use client';

import { useState } from 'react';

import { ScriptData } from '../_types';
import { Download } from './components';
import useExportScript from 'lib/hooks/useExportScript';
import Button from 'components/ui/Button';
import Dialog from 'components/ui/Dialog';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';
import { Checkbox } from 'components/shadcn_ui/checkbox';

type ExportFormat = 'docx' | 'pdf' | 'txt';

interface ExportOption {
  value: ExportFormat;
  label: string;
  description: string;
}

const exportOptions: ExportOption[] = [
  {
    value: 'docx',
    label: '.docx',
    description: 'Best for editing in Microsoft Word or Google Docs',
  },
  {
    value: 'pdf',
    label: '.pdf',
    description: 'Great for sharing or printing',
  },
  {
    value: 'txt',
    label: '.txt',
    description: 'Simple text file for quick copy-paste',
  },
];

export default function ExportScriptModal({
  trigger,
  script,
}: {
  trigger: React.ReactNode;
  script: ScriptData;
}) {
  const [open, setOpen] = useState(false);
  const [selectedFormat, setSelectedFormat] = useState<ExportFormat | null>(null);
  const { mutate: exportScript, isPending } = useExportScript();

  const handleFormatChange = (format: ExportFormat, checked: boolean) => {
    if (checked) {
      setSelectedFormat(format);
    } else {
      setSelectedFormat(null);
    }
  };

  const handleDownload = () => {
    if (!selectedFormat || !script?.uuid) return;

    exportScript(
      { uuid: script.uuid, format: selectedFormat },
      {
        onSuccess: async (data) => {
          try {
            const fileName = `${script.title || 'script'}-${script.uuid}.${data.format}`;
            const url = `${data.file_url}?t=${Date.now()}`;

            console.log('Attempting to download:', url);

            const response = await fetch(url);
            console.log('Response status:', response.status);
            console.log('Response headers:', [...response.headers.entries()]);

            if (!response.ok) {
              throw new Error(`HTTP error! status: ${response.status}`);
            }

            const blob = await response.blob();
            console.log('Blob size:', blob.size, 'Blob type:', blob.type);

            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = fileName;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(link.href);

            setOpen(false);
          } catch (error) {
            console.error('Download failed:', error);
            // Fallback: open in new tab
            window.open(`${data.file_url}?t=${Date.now()}`, '_blank');
          }
        },
        onError: (err) => {
          console.error('Export error:', err);
        },
      },
    );
  };

  const isFormatSelected = (format: ExportFormat) => selectedFormat === format;

  return (
    <Dialog
      open={open}
      setOpen={setOpen}
      trigger={trigger}
      title="Ready to save your script?"
      description="Choose a file format for your script"
      footer={
        <Row className="w-full gap-6">
          <Button
            variant="gray"
            onClick={() => {
              setOpen(false);
              setSelectedFormat(null);
            }}
          >
            <Text
              variant="base"
              className="font-extrabold [font-feature-settings:'liga'_off,'clig'_off]"
            >
              Cancel
            </Text>
          </Button>
          <Button
            type="submit"
            variant="green"
            onClick={handleDownload}
            disabled={!selectedFormat || isPending}
          >
            {Download} {isPending ? 'Downloading...' : 'Download'}
          </Button>
        </Row>
      }
    >
      {exportOptions.map((option) => (
        <Row key={option.value} className="my-2 justify-start">
          <Checkbox
            className="border-white"
            checked={isFormatSelected(option.value)}
            onCheckedChange={(checked) => handleFormatChange(option.value, checked as boolean)}
          />
          <Text variant="base">
            {option.label} — {option.description}
          </Text>
        </Row>
      ))}
    </Dialog>
  );
}
