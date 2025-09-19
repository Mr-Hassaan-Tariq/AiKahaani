import Image from 'next/image';
import Draft from '@assets/svg/draft.svg';
import { Download } from 'lucide-react';

import { ScriptCardProps } from '../_types';
import { basketIcon, Edit } from './components';
import DeleteScriptModal from './DeleteScriptModal';
import ExportScriptModal from './ExportScriptModal';
import Button from 'components/ui/Button';
import Card from 'components/ui/Card';
import Text from 'components/ui/Text';

export default function ScriptCard({ script, actions, className = '' }: ScriptCardProps) {
  // Handle both original API format and legacy format
  const isCompleted = script.status === 'saved';
  const scriptId = script.id || script.uuid;
  const scriptStatus = script.type;
  const scriptTitle = script.title;
  const lastEdited =
    script.lastEdited ||
    (script.modified
      ? new Date(script.modified).toLocaleDateString('en-US', {
          month: 'long',
          day: 'numeric',
          year: 'numeric',
        })
      : 'Unknown');
  const duration =
    script.duration ||
    (script.estimated_duration ? `${Math.round(script.estimated_duration)} min` : '0 min');
  const wordCount =
    script.wordCount || (script.word_count ? `${script.word_count} words` : '0 words');

  return (
    <Card className={`flex flex-col justify-between text-white lg:p-6 ${className}`}>
      <div>
        {!isCompleted && (
          <span className="inline-flex items-center gap-2 rounded-lg border border-[#BAFF3812] bg-[#303030] p-2 text-xs">
            <Image src={Draft} alt="Draft" width={16} height={16} />
            Draft – {scriptStatus}
          </span>
        )}

        {/* Title */}
        <h3 className="mt-3 line-clamp-2 text-xl font-semibold">{scriptTitle}</h3>

        {/* Metadata */}
        <div className="mt-3 space-y-2 text-sm text-gray-400">
          <Text className="text-white">
            Last edited: <span className="font-semibold">{lastEdited}</span>
          </Text>
          <Text className="text-white">
            Estimated video duration: <span className="font-semibold">{duration}</span>
          </Text>
          <Text className="text-white">
            Word count: <span className="font-semibold">{wordCount}</span>
          </Text>
        </div>
      </div>

      <div className="mt-5 flex items-center gap-3">
        <DeleteScriptModal
          trigger={<Button variant="gray">Delete {basketIcon}</Button>}
          script={script}
          actions={actions}
        />
        {isCompleted ? (
          <ExportScriptModal
            trigger={
              <Button variant="green">
                <Download size={16} className="mr-1" /> Export
              </Button>
            }
            script={script}
            actions={actions}
          />
        ) : (
          <Button
            className="bg-green-500 text-black hover:bg-green-600"
            onClick={() => actions.onEdit(scriptId || '')}
          >
            {Edit} Edit
          </Button>
        )}
      </div>
    </Card>
  );
}
