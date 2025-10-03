import { CardData } from './utils';

interface CardViewProps {
  card: CardData;
  onEdit: (card: CardData) => void;
}

export const CardView = ({ card, onEdit }: CardViewProps) => {
  return (
    <div
      className="-m-2 cursor-pointer rounded-lg p-2 px-4 font-figtree text-base text-white transition-colors duration-200 hover:bg-white/5"
      onClick={() => onEdit(card)}
    >
      <span className="font-semibold text-white/90">
        {card.id}. {card.title || 'Untitled Section'}
      </span>
      <span className="ml-2 text-white/70">
        {card.description || 'Click to add description...'}
      </span>
    </div>
  );
};
