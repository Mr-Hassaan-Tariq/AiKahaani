import { CardData } from './utils';

interface CardViewProps {
  card: CardData;
  onEdit: (card: CardData) => void;
}

export const CardView = ({ card, onEdit }: CardViewProps) => {
  return (
    <div
      className="cursor-pointer"
      onClick={() => onEdit(card)}
    >
      <p className="text-sm font-semibold text-foreground leading-snug">
        {card.title || 'Untitled Section'}
      </p>
      <p className="mt-1 text-[13px] text-muted-foreground leading-relaxed">
        {card.description || 'Click to add description…'}
      </p>
    </div>
  );
};
