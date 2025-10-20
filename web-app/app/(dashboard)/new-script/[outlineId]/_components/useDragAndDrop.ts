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

  // const handleDrop = (e: React.DragEvent, targetCardId: number) => {
  //   e.preventDefault();

  //   if (draggedCard && draggedCard !== targetCardId && dragOverIndex !== null) {
  //     const draggedIndex = cards.findIndex((card) => card.id === draggedCard);

  //     if (draggedIndex !== -1) {
  //       const newCards = reorderCards(cards, draggedIndex, dragOverIndex);
  //       setCards(newCards);

  //       // Calculate new section order based on the drag operation
  //       // We need to reorder the originalSectionOrder array based on the new card positions
  //       const newSectionOrder = [...originalSectionOrder];

  //       // Get the original section index that was dragged
  //       const draggedOriginalIndex = originalSectionOrder[draggedIndex];

  //       // Remove the dragged item from its original position
  //       newSectionOrder.splice(draggedIndex, 1);

  //       // Insert it at the new position
  //       newSectionOrder.splice(dragOverIndex, 0, draggedOriginalIndex);

  //       // Call the callback with new cards and section order
  //       if (onReorder) {
  //         onReorder(newCards, newSectionOrder);
  //       }
  //     }
  //   }

  //   setDraggedCard(null);
  //   setDragOverIndex(null);
  // };

  const handleDrop = (e: React.DragEvent, targetCardId: number) => {
    e.preventDefault();

    if (draggedCard && draggedCard !== targetCardId && dragOverIndex !== null) {
      const draggedIndex = cards.findIndex((card) => card.id === draggedCard);

      if (draggedIndex !== -1) {
        const newCards = reorderCards(cards, draggedIndex, dragOverIndex);
        setCards(newCards);

        // (KEEP local recalculation of section order if you need it later)
        // but DO NOT call onReorder here — remove live API trigger
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
