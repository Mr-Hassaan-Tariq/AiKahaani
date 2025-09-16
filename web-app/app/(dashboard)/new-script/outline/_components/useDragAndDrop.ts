import { CardData, reorderCards } from './utils';

export const useDragAndDrop = (
  cards: CardData[],
  setCards: (cards: CardData[]) => void,
  draggedCard: number | null,
  setDraggedCard: (id: number | null) => void,
  dragOverIndex: number | null,
  setDragOverIndex: (index: number | null) => void,
) => {
  const handleDragStart = (e: React.DragEvent, cardId: number) => {
    setDraggedCard(cardId);
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', cardId.toString());
  };

  const handleDragOver = (e: React.DragEvent, cardId: number, index: number) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';

    if (draggedCard && draggedCard !== cardId) {
      setDragOverIndex(index);
    }
  };

  const handleDragLeave = () => {
    setDragOverIndex(null);
  };

  const handleDrop = (e: React.DragEvent, targetCardId: number) => {
    e.preventDefault();

    if (draggedCard && draggedCard !== targetCardId && dragOverIndex !== null) {
      const draggedIndex = cards.findIndex((card) => card.id === draggedCard);

      if (draggedIndex !== -1) {
        const newCards = reorderCards(cards, draggedIndex, dragOverIndex);
        setCards(newCards);
      }
    }

    setDraggedCard(null);
    setDragOverIndex(null);
  };

  const handleDragEnd = () => {
    setDraggedCard(null);
    setDragOverIndex(null);
  };

  return {
    handleDragStart,
    handleDragOver,
    handleDragLeave,
    handleDrop,
    handleDragEnd,
  };
};
