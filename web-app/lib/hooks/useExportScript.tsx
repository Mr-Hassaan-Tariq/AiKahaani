'use client';

import { useMutation } from '@tanstack/react-query';
import Cookies from 'js-cookie';

import { baseUrl } from 'lib/api';
import { logger } from 'lib/logger';
import useToast from 'lib/utils/useToast';

export interface ExportScriptPayload {
  uuid: string;
  format: 'docx' | 'pdf' | 'txt';
}

async function fetchScriptContent(
  uuid: string,
  token: string,
): Promise<{ title: string; content: string }> {
  const base = baseUrl.replace(/\/$/, '');

  // Try full script first, then fall back to outline
  const scriptRes = await fetch(`${base}/v1/scripts/scripts/${uuid}`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (scriptRes.ok) {
    const json = await scriptRes.json();
    const data = json.data ?? json;
    const sections: any[] = data.sections ?? [];
    const sectionText = sections
      .map((s: any) => `## ${s.title ?? ''}\n\n${s.content ?? ''}`)
      .join('\n\n---\n\n');
    const content = data.content ?? sectionText ?? '';
    return { title: data.title ?? 'script', content };
  }

  const outlineRes = await fetch(`${base}/v1/scripts/outlines/${uuid}`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (outlineRes.ok) {
    const json = await outlineRes.json();
    const data = json.data ?? json;
    const sections: any[] = data.outline_data?.sections ?? [];
    const sectionText = sections
      .map(
        (s: any) =>
          `## ${s.title ?? ''}\n\n${s.description ?? ''}\n\n${(s.key_points ?? []).map((kp: string) => `- ${kp}`).join('\n')}`,
      )
      .join('\n\n---\n\n');
    const content = data.outline_text ?? sectionText ?? '';
    return { title: data.title ?? 'outline', content };
  }

  throw new Error('Script not found.');
}

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.style.display = 'none';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  setTimeout(() => URL.revokeObjectURL(url), 5000);
}

async function exportScript({ uuid, format }: ExportScriptPayload): Promise<{ format: string }> {
  if (process.env.NEXT_PUBLIC_BYPASS_AUTH === 'true') {
    const { mockScript } = await import('lib/mockData');
    const text = [
      mockScript.title,
      '',
      ...mockScript.sections.map((s: any) => `## ${s.title}\n\n${s.content}`),
    ].join('\n\n');
    downloadBlob(new Blob([text], { type: 'text/plain' }), `${mockScript.title}.txt`);
    return { format };
  }

  const token = Cookies.get('access_token');
  if (!token) throw new Error('Authentication token not found. Please log in again.');

  const { title, content } = await fetchScriptContent(uuid, token);
  const safeName = title.replace(/[^a-z0-9_\-\s]/gi, '').trim() || 'script';

  if (format === 'txt') {
    downloadBlob(new Blob([content], { type: 'text/plain;charset=utf-8' }), `${safeName}.txt`);
    return { format };
  }

  if (format === 'pdf') {
    const html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>${title}</title>
  <style>
    body { font-family: Georgia, serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.7; color: #111; }
    h1 { font-size: 24px; margin-bottom: 8px; }
    h2 { font-size: 18px; margin-top: 32px; margin-bottom: 8px; }
    hr { border: none; border-top: 1px solid #ddd; margin: 24px 0; }
    p { margin: 0 0 12px; }
    ul { padding-left: 20px; }
  </style>
</head>
<body>
  <h1>${title}</h1>
  ${content
    .split('\n')
    .map((line) => {
      if (line.startsWith('## ')) return `<h2>${line.slice(3)}</h2>`;
      if (line === '---') return '<hr/>';
      if (line.startsWith('- ')) return `<li>${line.slice(2)}</li>`;
      if (line.trim() === '') return '<br/>';
      return `<p>${line}</p>`;
    })
    .join('\n')}
</body>
</html>`;
    const win = window.open('', '_blank');
    if (!win) throw new Error('Popup blocked. Please allow popups and try again.');
    win.document.write(html);
    win.document.close();
    win.focus();
    win.print();
    return { format };
  }

  if (format === 'docx') {
    // Client-side DOCX using a simple XML-based Word format
    const escaped = content.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

    const paragraphs = escaped.split('\n').map((line) => {
      if (line.startsWith('## ')) {
        return `<w:p><w:pPr><w:pStyle w:val="Heading2"/></w:pPr><w:r><w:t>${line.slice(3)}</w:t></w:r></w:p>`;
      }
      if (line.trim() === '' || line === '---') {
        return '<w:p><w:r><w:t></w:t></w:r></w:p>';
      }
      return `<w:p><w:r><w:t xml:space="preserve">${line}</w:t></w:r></w:p>`;
    });

    const docxml = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:body>
<w:p><w:pPr><w:pStyle w:val="Title"/></w:pPr><w:r><w:t>${title.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')}</w:t></w:r></w:p>
${paragraphs.join('\n')}
</w:body>
</w:document>`;

    downloadBlob(
      new Blob([docxml], {
        type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      }),
      `${safeName}.docx`,
    );
    return { format };
  }

  throw new Error(`Unsupported format: ${format}`);
}

export default function useExportScript() {
  const toast = useToast();

  return useMutation({
    mutationFn: exportScript,
    onSuccess: ({ format }) => {
      if (format !== 'pdf') {
        toast.success('Export Successful', `Your script has been exported as .${format}.`);
      }
    },
    onError: (error: Error) => {
      logger.error('Export failed:', error);
      toast.error('Export Failed', error.message || 'Failed to export script. Please try again.');
    },
  });
}
