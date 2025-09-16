'use client';

import { useState } from 'react';
import { ArrowLeft, Edit2, PlusCircle, RefreshCcw } from 'lucide-react';

import { CardView } from './_components/CardView';
import { directFileIcon, dummyOutline } from './_components/components';
import { SortableCard } from './_components/SortableCard';
import { useCardManager } from './_components/useCardManager';
import { useDragAndDrop } from './_components/useDragAndDrop';
import Button from 'components/ui/Button';
import Card from 'components/ui/Card';
import Col from 'components/ui/Col';
import Row from 'components/ui/Row';

export default function OutlineComponent() {
  const [edit, setEdit] = useState(false);

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
  } = useCardManager(dummyOutline);

  const { handleDragStart, handleDragOver, handleDragLeave, handleDrop, handleDragEnd } =
    useDragAndDrop(cards, setCards, draggedCard, setDraggedCard, dragOverIndex, setDragOverIndex);

  return (
    <>
      <Col className="scrollbar max-h-[calc(100vh-200px)] w-full space-y-3 overflow-hidden overflow-y-auto">
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
              >
                <div className="p-4">
                  <CardView card={card} onEdit={startEditing} />
                </div>
              </Card>
            ))}
      </Col>

      {edit ? (
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
            onClick={() => setEdit(false)}
            className="w-full transition-colors duration-200 hover:bg-white/90 lg:w-fit"
          >
            {directFileIcon} Save Changes
          </Button>
        </Row>
      ) : (
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
            >
              <RefreshCcw size={20} className="min-w-5" /> Regenerate
            </Button>
          </Row>
          <Button className="w-full transition-colors duration-200 hover:bg-white/90 lg:w-fit">
            {directFileIcon} Generate the script
          </Button>
        </Row>
      )}
    </>
  );
}
