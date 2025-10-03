import { useEffect, useRef, useState } from 'react';

import { CardData, EditValues, ValidationErrors } from './utils';

export const useCardManager = (initialCards: CardData[], onDelete?: (cardId: number) => void) => {
  const [cards, setCards] = useState<CardData[]>(initialCards);
  const [editingCard, setEditingCard] = useState<number | null>(null);
  const [editValues, setEditValues] = useState<EditValues>({ title: '', description: '' });
  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({
    title: false,
    description: false,
  });
  const [draggedCard, setDraggedCard] = useState<number | null>(null);
  const [dragOverIndex, setDragOverIndex] = useState<number | null>(null);

  const titleInputRef = useRef<HTMLInputElement | null>(null);
  const descriptionInputRef = useRef<HTMLTextAreaElement | null>(null);

  // Auto-focus on title input when editing starts
  useEffect(() => {
    if (editingCard && titleInputRef.current) {
      titleInputRef.current.focus();
      titleInputRef.current.select();
    }
  }, [editingCard]);

  const updateCard = (id: number, field: 'title' | 'description', value: string) => {
    setCards((prevCards) =>
      prevCards.map((card) => (card.id === id ? { ...card, [field]: value } : card)),
    );
  };

  const addNewCard = () => {
    const newId = Math.max(...cards.map((card) => card.id), 0) + 1;
    const newCard: CardData = {
      id: newId,
      title: '',
      description: '',
      keyPoints: [],
      timing: '',
      transition: '',
    };

    setCards((prevCards) => [...prevCards, newCard]);
    setEditingCard(newId);
    setEditValues({ title: '', description: '' });
    setValidationErrors({ title: false, description: false });
  };

  const startEditing = (card: CardData) => {
    setEditingCard(card.id);
    setEditValues({ title: card.title, description: card.description });
    setValidationErrors({ title: false, description: false });
  };

  const saveChanges = () => {
    if (editingCard && editValues.title.trim() && editValues.description.trim()) {
      updateCard(editingCard, 'title', editValues.title.trim());
      updateCard(editingCard, 'description', editValues.description.trim());
      setEditingCard(null);
      setValidationErrors({ title: false, description: false });
    }
  };

  const cancelEditing = () => {
    setEditingCard(null);
    setEditValues({ title: '', description: '' });
    setValidationErrors({ title: false, description: false });
  };

  const deleteCard = (id: number) => {
    if (onDelete) {
      onDelete(id);
    } else {
      // Fallback to local deletion if no callback provided
      setCards((prevCards) => prevCards.filter((card) => card.id !== id));
    }
  };

  const handleInputChange = (field: 'title' | 'description', value: string) => {
    setEditValues((prev) => ({ ...prev, [field]: value }));

    // Clear validation error when user starts typing
    if (validationErrors[field] && value.trim().length > 0) {
      setValidationErrors((prev) => ({ ...prev, [field]: false }));
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      e.preventDefault();
      saveChanges();
    } else if (e.key === 'Escape') {
      e.preventDefault();
      cancelEditing();
    }
  };

  return {
    cards,
    setCards,
    editingCard,
    editValues,
    validationErrors,
    draggedCard,
    setDraggedCard,
    dragOverIndex,
    setDragOverIndex,
    titleInputRef,
    descriptionInputRef,
    addNewCard,
    startEditing,
    saveChanges,
    cancelEditing,
    deleteCard,
    handleInputChange,
    handleKeyDown,
  };
};
