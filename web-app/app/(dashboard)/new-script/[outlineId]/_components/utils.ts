export interface CardData {
  id: number;
  title: string;
  description: string;
  keyPoints: string[];
  timing: string;
  transition: string;
}

export interface EditValues {
  title: string;
  description: string;
}

export interface ValidationErrors {
  title: boolean;
  description: boolean;
}

// Generate unique ID for new cards
export const generateNewId = (cards: CardData[]): number => {
  const maxId = Math.max(...cards.map((card) => card.id), 0);
  return maxId + 1;
};

// Validate form fields
export const validateFields = (editValues: EditValues): ValidationErrors => {
  const titleValid = editValues.title.trim().length > 0;
  const descriptionValid = editValues.description.trim().length > 0;

  return {
    title: !titleValid,
    description: !descriptionValid,
  };
};

// Check if form is valid
export const isFormValid = (editValues: EditValues): boolean => {
  return editValues.title.trim().length > 0 && editValues.description.trim().length > 0;
};

// Drag and drop utilities
export const reorderCards = (
  cards: CardData[],
  draggedIndex: number,
  targetIndex: number,
): CardData[] => {
  const newCards = [...cards];
  const draggedItem = newCards[draggedIndex];

  // Remove the dragged item
  newCards.splice(draggedIndex, 1);

  // Calculate the new insertion index (always insert after target)
  let newIndex = targetIndex;
  if (draggedIndex < targetIndex) {
    newIndex = targetIndex; // Insert after the target
  } else {
    newIndex = targetIndex + 1; // Insert after the target
  }

  // Insert at the new position
  newCards.splice(newIndex, 0, draggedItem);

  return newCards;
};
