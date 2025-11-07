'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Edit2, PlusCircle, RefreshCcw } from 'lucide-react';

import { LoadingScreen } from '../_components/components';
import { FormType, OutlineType } from '../types';
import { CardView } from './_components/CardView';
import { directFileIcon } from './_components/components';
import { SortableCard } from './_components/SortableCard';
import { useCardManager } from './_components/useCardManager';
import { useDragAndDrop } from './_components/useDragAndDrop';
import useGenerateOutline from 'lib/hooks/useGenerateOutline';
import useGenerateScript from 'lib/hooks/useGenerateScript';
import useUpdateOutline from 'lib/hooks/useUpdateOutline';
import useUpdateOutlineOrder from 'lib/hooks/useUpdateOutlineOrder';
import { logger } from 'lib/logger';
import useToast from 'lib/utils/useToast';
import Button from 'components/ui/Button';
import Card from 'components/ui/Card';
import Col from 'components/ui/Col';
import PageLoader from 'components/ui/PageLoader';
import Row from 'components/ui/Row';

// Convert outline data to card format
const convertOutlineToCards = (outline: OutlineType) => {
  // Add null checks and fallbacks
  if (!outline || !outline.outline_data || !outline.outline_data.sections) {
    return [];
  }

  // Use section_order if available, otherwise use default order
  const sectionOrder =
    outline.section_order || outline.outline_data.sections.map((_, index) => index);

  // Reorder sections based on section_order
  const orderedSections = sectionOrder
    .map((index) => outline.outline_data.sections[index])
    .filter(Boolean);

  return orderedSections.map((section, index) => ({
    id: index + 1,
    title: section.title || '',
    description: section.description || '',
    keyPoints: section.key_points || [],
    timing: section.timing || '',
    transition: section.transition || '',
  }));
};

// Convert cards back to outline format
const convertCardsToOutline = (cards: any[], originalOutline: OutlineType) => {
  const sections = cards.map((card) => ({
    title: card.title || '',
    description: card.description || '',
    key_points: card.keyPoints || [],
    timing: card.timing || '',
    transition: card.transition || '',
  }));

  return {
    ...originalOutline,
    outline_data: {
      ...originalOutline.outline_data,
      sections,
    },
  };
};

export default function OutlineComponent({ outline }: { outline: OutlineType }) {
  const toast = useToast();
  const router = useRouter();
  const [edit, setEdit] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const { isPending, mutate: updateOutline } = useUpdateOutline();
  const { isPending: isUpdatingOrder, mutate: updateOutlineOrder } = useUpdateOutlineOrder();
  const { isPending: isGeneratingScript, mutate: generateScript } = useGenerateScript();
  const { isPending: isRegeneratingOutline, mutate: generateOutline } = useGenerateOutline();

  // Convert outline to cards format with fallback
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const initialCards = outline ? convertOutlineToCards(outline) : [];

  // Handle delete callback
  const handleDelete = (cardId: number) => {
    if (!outline) return;

    // Find the card to delete
    const cardToDelete = cards.find((card) => card.id === cardId);
    if (!cardToDelete) return;

    // Find the index of the card in the current cards array
    const cardIndex = cards.findIndex((card) => card.id === cardId);

    // Remove the card from local state
    const newCards = cards.filter((card) => card.id !== cardId);
    setCards(newCards);

    // Calculate new section_order by removing the deleted section's index
    // Since cards are ordered according to section_order, we can safely remove by index
    const newSectionOrder = [...(outline.section_order || [])];
    if (cardIndex < newSectionOrder.length) {
      newSectionOrder.splice(cardIndex, 1);
    }
    // Convert remaining cards back to outline format
    const updatedOutlineData = convertCardsToOutline(newCards, outline);

    // Call API to update the outline
    updateOutlineOrder(
      {
        uuid: outline.uuid,
        sectionOrder: newSectionOrder,
        outlineData: updatedOutlineData.outline_data,
      },
      {
        onSuccess: () => {
          toast.success('Success', 'Section deleted successfully');
        },
        onError: (error) => {
          logger.error(error);
          toast.error('Something went wrong', 'Error deleting section');
          // Revert the local state on error
          setCards(cards);
        },
      },
    );
  };

  const {
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
  } = useCardManager(initialCards, handleDelete);

  // // Handle reorder callback
  // const handleReorder = (newCards: any[], sectionOrder: number[]) => {
  //   if (!outline) return;

  //   // Convert cards back to outline format with reordered sections
  //   const reorderedOutlineData = convertCardsToOutline(newCards, outline);

  //   // Call API to update the outline order
  //   updateOutlineOrder(
  //     {
  //       uuid: outline.uuid,
  //       sectionOrder,
  //       outlineData: reorderedOutlineData.outline_data,
  //     },
  //     {
  //       onSuccess: () => {
  //         toast.success('Success', 'Section order updated successfully');
  //       },
  //       onError: (error) => {
  //         logger.error(error);
  //         toast.error('Something went wrong', 'Error updating section order');
  //         // Revert the local state on error
  //         setCards(cards);
  //       },
  //     },
  //   );
  // };

  const { handleDragStart, handleDragOver, handleDragLeave, handleDrop, handleDragEnd } =
    useDragAndDrop(cards, setCards, draggedCard, setDraggedCard, dragOverIndex, setDragOverIndex);

  // Track changes
  useEffect(() => {
    const hasChanges = JSON.stringify(cards) !== JSON.stringify(initialCards);
    setHasChanges(hasChanges);
  }, [cards, initialCards]);

  // Handle save changes
  const handleSaveChanges = () => {
    if (!outline) return;

    const invalidCard = cards.find((card) => !card.title?.trim() || !card.description?.trim());

    if (invalidCard) {
      toast.error(
        'Missing Fields',
        'Every section must have a title and description before saving.',
      );
      return;
    }

    const updatedOutline = convertCardsToOutline(cards, outline);

    updateOutline(updatedOutline, {
      onSuccess: () => {
        toast.success('Success', 'Outline updated successfully');
        setHasChanges(false);
        setEdit(false);
      },
      onError: (error) => {
        logger.error(error);
        toast.error('Something went wrong', 'Error updating outline');
      },
    });
  };

  // Handle regenerate
  // inside OutlineComponent — replace handleRegenerate with this:

  const handleRegenerate = async () => {
    if (!outline) return;

    // Attempt to read saved payload from localStorage
    let savedRaw: string | null = null;
    try {
      savedRaw =
        typeof window !== 'undefined' ? localStorage.getItem('last_outline_payload') : null;
    } catch (e) {
      logger.warn('Could not read last_outline_payload from localStorage', e);
      savedRaw = null;
    }

    let payloadToSend: any = null; // either object or FormData

    if (savedRaw) {
      try {
        const saved = JSON.parse(savedRaw);
        if (saved && saved.hasImageFile && saved.data) {
          // Reconstruct FormData from saved data + images (data URLs)
          const fd = new FormData();
          fd.append('description', saved.data.description ?? '');

          // tones (array)
          (saved.data.tones || []).forEach((t: any) => fd.append('tones', String(t)));

          if (saved.data.template_style) {
            fd.append('template_style', String(saved.data.template_style));
          } else {
            fd.append('min_length', String(saved.data.min_length ?? 0));
            fd.append('max_length', String(saved.data.max_length ?? 500));
          }
          fd.append('title', String(saved.data.title ?? ''));

          if (saved.data.niche_id) {
            fd.append('niche_id', String(saved.data.niche_id));
          }

          // Append link/article items
          (saved.data.linkItems || []).forEach((l: string) => fd.append('youtube_url', l));
          (saved.data.articleItems || []).forEach((a: string) => fd.append('article_url', a));

          // Recreate File objects from data URLs and append them
          const images = saved.data.images || [];
          for (const img of images) {
            try {
              // img.dataUrl is something like "data:image/jpeg;base64,...."
              const res = await fetch(img.dataUrl);
              const blob = await res.blob();
              const file = new File([blob], img.name || 'image', { type: img.type || blob.type });
              fd.append('image', file);
            } catch (err) {
              logger.warn('Failed to reconstruct one image from saved payload', err);
              // continue without this file
            }
          }

          payloadToSend = fd;
        } else if (saved && saved.hasImageFile === false && saved.payload) {
          payloadToSend = saved.payload;
        } else if (saved && saved.data && !saved.hasImageFile) {
          // fallback in case of different shape
          payloadToSend = saved.data;
        }
      } catch (e) {
        logger.warn('Could not parse last_outline_payload from localStorage', e);
        payloadToSend = null;
      }
    }

    // If we didn't get a saved payload, fall back to original behavior deriving payload from outline
    if (!payloadToSend) {
      const payload: Partial<FormType> = {
        description: outline.description || '',
        tones: outline.tones ? outline.tones.map((tone: any) => tone.id) : [],
        template_style: outline.template_style ?? undefined,
        min_length: outline.min_length || 0,
        max_length: outline.max_length || 500,
        title: outline.title || '',
      };

      // try to use saved draft_description if present
      try {
        const saved = localStorage.getItem('draft_description');
        if (saved && saved.trim().length > 0) {
          payload.description = saved;
        }
      } catch (e) {
        logger.warn('Could not read draft_description from localStorage', e);
      }

      payloadToSend = payload;
    }

    generateOutline(payloadToSend, {
      onSuccess: (data) => {
        toast.success('Success', 'Outline regenerated successfully');
        router.replace(`/new-script/${data.outline.uuid}`);
      },
      onError: (error) => {
        logger.error(error);
        toast.error('Something went wrong', 'Error regenerating outline');
      },
    });
  };

  // Handle generate script
  const handleGenerateScript = () => {
    if (!outline) return;
    generateScript(outline.uuid, {
      onSuccess: (data) => {
        toast.success('Success', 'Script generated successFully');
        router.replace(`/new-script/script/${data.script.uuid}`);
      },
      onError: (error) => {
        logger.error(error);
        toast.error('Something went wrong', 'Error in generation script');
      },
    });
  };

  // Show loading state if outline is not available
  if (!outline) {
    return (
      <div className="flex h-64 items-center justify-center">
        <p className="text-white/70">Loading outline...</p>
      </div>
    );
  }

  const isBusy = isRegeneratingOutline || isGeneratingScript;

  return (
    <>
      {isPending || (isUpdatingOrder && <PageLoader size="lg" color="white" />)}
      <Col className="scrollbar max-h-[calc(100vh-200px)] w-full space-y-3 overflow-hidden overflow-y-auto">
        {isRegeneratingOutline || isGeneratingScript ? (
          <LoadingScreen />
        ) : (
          // eslint-disable-next-line react/jsx-no-useless-fragment
          <>
            {edit
              ? cards.map((card, index) => (
                  <SortableCard
                    key={card.id}
                    card={card}
                    index={index}
                    isEditing={editingCard === card.id}
                    editValues={editValues}
                    validationErrors={validationErrors}
                    isDragged={draggedCard === card.id}
                    isDragOver={dragOverIndex === index}
                    showDropIndicator={dragOverIndex === index}
                    titleInputRef={titleInputRef}
                    descriptionInputRef={descriptionInputRef}
                    onDragStart={(e) => handleDragStart(e, card.id)}
                    onDragOver={(e) => handleDragOver(e, card.id, index)}
                    onDragLeave={handleDragLeave}
                    onDrop={(e) => handleDrop(e, card.id)}
                    onDragEnd={handleDragEnd}
                    onEdit={startEditing}
                    onInputChange={handleInputChange}
                    onKeyDown={handleKeyDown}
                    onSave={saveChanges}
                    onCancel={cancelEditing}
                    onDelete={deleteCard}
                  />
                ))
              : cards.map((card) => (
                  <Card
                    key={card.id}
                    className="group cursor-pointer border border-white/20 bg-white/10 backdrop-blur-sm transition-all duration-200 hover:bg-white/15 hover:shadow-lg hover:shadow-white/10"
                    onClick={() => startEditing(card)}
                  >
                    <div className="">
                      <CardView card={card} onEdit={startEditing} />
                    </div>
                  </Card>
                ))}
          </>
        )}
      </Col>

      {edit ? (
        isBusy ? null : (
          <Row className="mt-6">
            <Row className="space-x-3">
              <Button
                variant="gray"
                onClick={() => setEdit(false)}
                className="transition-colors duration-200 hover:bg-white/20"
              >
                <ArrowLeft size={20} className="min-w-5" /> Back
              </Button>
              <Button
                variant="gray"
                className="min-w-[200px] transition-colors duration-200 hover:bg-white/20"
                onClick={addNewCard}
              >
                <PlusCircle size={20} className="min-w-5" /> Add new section
              </Button>
            </Row>
            <Button
              onClick={handleSaveChanges}
              disabled={!hasChanges}
              className={`w-full transition-colors duration-200 lg:w-fit ${
                hasChanges ? 'hover:bg-white/90' : 'cursor-not-allowed opacity-50'
              }`}
            >
              {directFileIcon} Save Changes {hasChanges && ''}
            </Button>
          </Row>
        )
      ) : isBusy ? null : (
        <Row className="mt-6 w-full flex-col space-y-3 lg:flex-row lg:space-y-0">
          <Row className="space-x-3">
            <Button
              variant="gray"
              onClick={() => setEdit(true)}
              className="transition-colors duration-200 hover:bg-white/20"
            >
              <Edit2 size={20} className="min-w-5" /> Edit
            </Button>
            <Button
              variant="gray"
              className="min-w-[166px] transition-colors duration-200 hover:bg-white/20"
              onClick={handleRegenerate}
            >
              <RefreshCcw size={20} className="min-w-5" /> Regenerate
            </Button>
          </Row>
          <Button
            className="w-full transition-colors duration-200 hover:bg-white/90 lg:w-fit"
            onClick={handleGenerateScript}
          >
            {directFileIcon} Generate the script
          </Button>
        </Row>
      )}
    </>
  );
}
