import Image from 'next/image';
import Draft from '@assets/svg/draft.svg';
import { Download } from 'lucide-react';

import { ScriptCardProps } from '../_types';
import { basketIcon, Edit } from './components';
import DeleteScriptModal from './DeleteScriptModal';
import Button from 'components/ui/Button';
import Card from 'components/ui/Card';
import Text from 'components/ui/Text';

export default function ScriptCard({ script, actions, className = '' }: ScriptCardProps) {
  const isCompleted = script.status === 'Completed';

  return (
    <Card className={`flex flex-col justify-between text-white lg:p-6 ${className}`}>
      <div>
        {!isCompleted && (
          <span className="inline-flex items-center gap-2 rounded-lg border border-[#BAFF3812] bg-[#303030] p-2 text-xs">
            <Image src={Draft} alt="Draft" width={16} height={16} />
            Draft – {script.status}
          </span>
        )}

        {/* Title */}
        <h3 className="mt-3 line-clamp-2 text-xl font-semibold">{script.title}</h3>

        {/* Metadata */}
        <div className="mt-3 space-y-2 text-sm text-gray-400">
          <Text className="text-white">
            Last edited: <span className="font-semibold">{script.lastEdited}</span>
          </Text>
          <Text className="text-white">
            Estimated video duration: <span className="font-semibold">{script.duration}</span>
          </Text>
          <Text className="text-white">
            Word count: <span className="font-semibold">{script.wordCount}</span>
          </Text>
        </div>
      </div>

      <div className="mt-5 flex items-center gap-3">
        <DeleteScriptModal
          trigger={
            <Button variant="gray" onClick={() => actions.onDelete(script.id)}>
              Delete {basketIcon}
            </Button>
          }
        />
        {isCompleted ? (
          <Button
            className="bg-green-500 text-black hover:bg-green-600"
            onClick={() => actions.onExport?.(script.id)}
          >
            <Download size={16} className="mr-1" /> Export
          </Button>
        ) : (
          <Button
            className="bg-green-500 text-black hover:bg-green-600"
            onClick={() => actions.onEdit(script.id)}
          >
            {Edit} Edit
          </Button>
        )}
      </div>
    </Card>
  );
}
