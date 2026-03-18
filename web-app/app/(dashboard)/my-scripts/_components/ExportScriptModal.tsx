'use client';

import { useState } from 'react';
import { Download } from 'lucide-react';

import { ScriptData } from '../_types';
import useExportScript from 'lib/hooks/useExportScript';
import { logger } from 'lib/logger';
import { Button } from 'components/ui/Button';
import Dialog from 'components/ui/Dialog';
import { Checkbox } from 'components/shadcn_ui/checkbox';

type ExportFormat = 'docx' | 'pdf' | 'txt';

const exportOptions = [
  {
    value: 'docx' as ExportFormat,
    label: '.docx',
    description: 'Best for editing in Word or Google Docs',
  },
  { value: 'pdf' as ExportFormat, label: '.pdf', description: 'Great for sharing or printing' },
  {
    value: 'txt' as ExportFormat,
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

  const handleDownload = () => {
    if (!selectedFormat || !script?.uuid) return;
    exportScript(
      { uuid: script.uuid, format: selectedFormat },
      {
        onSuccess: (data) => {
          if (data.format === 'docx') {
            const a = document.createElement('a');
            a.href = data.file_url;
            a.download = `${script.title || 'script'}-${script.uuid}.${data.format}`;
            a.style.display = 'none';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
          } else {
            window.open(data.file_url, '_blank');
          }
          setOpen(false);
        },
        onError: (err) => {
          logger.error('Export error:', err);
        },
      },
    );
  };

  return (
    <Dialog
      open={open}
      setOpen={(v) => {
        setOpen(v);
        if (!v) setSelectedFormat(null);
      }}
      trigger={trigger}
      title="Export script"
      description="Choose a file format for your script."
      footer={
        <div className="flex w-full gap-3">
          <Button
            variant="outline"
            className="flex-1"
            onClick={() => {
              setOpen(false);
              setSelectedFormat(null);
            }}
          >
            Cancel
          </Button>
          <Button
            className="flex-1"
            onClick={handleDownload}
            disabled={!selectedFormat || isPending}
            loading={isPending}
          >
            <Download className="h-4 w-4" /> Download
          </Button>
        </div>
      }
    >
      <div className="my-2 flex flex-col gap-3">
        {exportOptions.map((option) => (
          <label
            key={option.value}
            className="flex cursor-pointer items-center gap-3 rounded-lg border border-border p-3 transition-colors hover:bg-accent has-[:checked]:border-primary has-[:checked]:bg-accent"
          >
            <Checkbox
              checked={selectedFormat === option.value}
              onCheckedChange={(checked) => setSelectedFormat(checked ? option.value : null)}
            />
            <div>
              <p className="text-sm font-medium text-foreground">{option.label}</p>
              <p className="text-xs text-muted-foreground">{option.description}</p>
            </div>
          </label>
        ))}
      </div>
    </Dialog>
  );
}
