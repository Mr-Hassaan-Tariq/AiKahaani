import { CardData } from './utils';

interface CardViewProps {
  card: CardData;
  onEdit: (card: CardData) => void;
}

export const CardView = ({ card, onEdit }: CardViewProps) => {
  return (
    <div className="cursor-pointer" onClick={() => onEdit(card)}>
      <p className="text-sm font-semibold leading-snug text-foreground">
        {card.title || 'Untitled Section'}
      </p>
      <p className="mt-1 text-[13px] leading-relaxed text-muted-foreground">
        {card.description || 'Click to add description…'}
      </p>
    </div>
  );
};
