import { CardData } from './utils';

interface CardViewProps {
  card: CardData;
  onEdit: (card: CardData) => void;
}

export const CardView = ({ card, onEdit }: CardViewProps) => {
  return (
    <div
      className="cursor-pointer rounded-lg p-1 transition-colors hover:bg-accent/50"
      onClick={() => onEdit(card)}
    >
      <div className="flex items-baseline gap-2">
        <span className="shrink-0 text-xs font-semibold text-primary">
          {String(card.id).padStart(2, '0')}
        </span>
        <span className="text-sm font-semibold text-foreground">
          {card.title || 'Untitled Section'}
        </span>
        <span className="ml-1 text-sm text-muted-foreground">
          {card.description || 'Click to add description…'}
        </span>
      </div>
    </div>
  );
};
