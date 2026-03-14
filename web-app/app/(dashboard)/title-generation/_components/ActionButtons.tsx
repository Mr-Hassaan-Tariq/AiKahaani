import { Edit2, RefreshCcw } from 'lucide-react';

import { Button } from 'components/ui/Button';

export default function ActionButtons({ isGenerating, onEdit, onRegenerate }: {
  isGenerating: boolean;
  onEdit: () => void;
  onRegenerate: () => void;
}) {
  return (
    <div className="flex w-full gap-3">
      <Button variant="outline" className="flex-1" onClick={onEdit}>
        <Edit2 className="h-4 w-4" /> Edit info
      </Button>
      <Button
        variant="outline"
        className="flex-1"
        onClick={onRegenerate}
        loading={isGenerating}
        disabled={isGenerating}
      >
        <RefreshCcw className="h-4 w-4" /> Regenerate
      </Button>
    </div>
  );
}
