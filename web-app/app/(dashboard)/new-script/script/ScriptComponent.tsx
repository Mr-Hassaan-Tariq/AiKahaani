'use client';

import { useEffect, useRef, useState } from 'react';
import { ArrowLeft, Check, Edit2, PlusCircle, RefreshCcw, Trash2, X } from 'lucide-react';

import { directFileIcon, dummyOutline } from '../outline/_components/components';
import DeleteOutlineSection from '../outline/_components/DeleteOutlineSection';
import Button from 'components/ui/Button';
import Card from 'components/ui/Card';
import Col from 'components/ui/Col';
import Row from 'components/ui/Row';

export default function ScriptComponent() {
  const [edit, setEdit] = useState(false);
  const [state, setState] = useState(dummyOutline);
  const [editingCard, setEditingCard] = useState<number | null>(null);
  const [editValues, setEditValues] = useState<{ title: string; description: string }>({
    title: '',
    description: '',
  });
  const [validationErrors, setValidationErrors] = useState<{
    title: boolean;
    description: boolean;
  }>({
    title: false,
    description: false,
  });
  const titleInputRef = useRef<HTMLInputElement>(null);
  const descriptionInputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-sync function
  const updateCard = (id: number, field: 'title' | 'description', value: string) => {
    setState((prevState) =>
      prevState.map((card) => (card.id === id ? { ...card, [field]: value } : card)),
    );
  };

  // Generate unique ID for new cards
  const generateNewId = () => {
    const maxId = Math.max(...state.map((card) => card.id), 0);
    return maxId + 1;
  };

  // Add new empty card
  const addNewCard = () => {
    const newId = generateNewId();
    const newCard = {
      id: newId,
      title: '',
      description: '',
    };

    setState((prevState) => [...prevState, newCard]);
    setEditingCard(newId);
    setEditValues({ title: '', description: '' });
    setValidationErrors({ title: false, description: false });
  };

  // Start editing a card
  const startEditing = (card: { id: number; title: string; description: string }) => {
    setEditingCard(card.id);
    setEditValues({ title: card.title, description: card.description });
    setValidationErrors({ title: false, description: false });
  };

  // Validate form fields
  const validateFields = () => {
    const titleValid = editValues.title.trim().length > 0;
    const descriptionValid = editValues.description.trim().length > 0;

    setValidationErrors({
      title: !titleValid,
      description: !descriptionValid,
    });

    return titleValid && descriptionValid;
  };

  // Save changes and exit edit mode
  const saveChanges = () => {
    if (editingCard) {
      if (validateFields()) {
        updateCard(editingCard, 'title', editValues.title.trim());
        updateCard(editingCard, 'description', editValues.description.trim());
        setEditingCard(null);
        setValidationErrors({ title: false, description: false });
      }
    }
  };

  // Cancel editing
  const cancelEditing = () => {
    setEditingCard(null);
    setEditValues({ title: '', description: '' });
    setValidationErrors({ title: false, description: false });
  };

  // Handle keyboard events
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      e.preventDefault();
      saveChanges();
    } else if (e.key === 'Escape') {
      e.preventDefault();
      cancelEditing();
    }
  };

  // Handle input changes with validation
  const handleInputChange = (field: 'title' | 'description', value: string) => {
    setEditValues((prev) => ({ ...prev, [field]: value }));

    // Clear validation error when user starts typing
    if (validationErrors[field] && value.trim().length > 0) {
      setValidationErrors((prev) => ({ ...prev, [field]: false }));
    }
  };

  // Auto-focus on title input when editing starts
  useEffect(() => {
    if (editingCard && titleInputRef.current) {
      titleInputRef.current.focus();
      titleInputRef.current.select();
    }
  }, [editingCard]);

  return (
    <>
      <Col className="scrollbar h-full w-full space-y-3">
        {edit
          ? state.map((e) => (
              <Card
                key={e.id}
                className="group relative flex flex-row items-center border border-white/20 bg-white/10 backdrop-blur-sm transition-all duration-200 hover:bg-white/15 hover:shadow-lg hover:shadow-white/10"
              >
                {/* Content */}
                <div className="ml-8 w-full py-4 pr-4">
                  {editingCard === e.id ? (
                    // Edit Mode
                    <div className="space-y-3">
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-semibold text-white/90">{e.id}.</span>
                        <div className="flex-1">
                          <input
                            ref={titleInputRef}
                            type="text"
                            value={editValues.title}
                            onChange={(e) => handleInputChange('title', e.target.value)}
                            onKeyDown={handleKeyDown}
                            className={`w-full rounded-lg border px-3 py-2 text-white placeholder-white/50 transition-colors duration-200 focus:outline-none focus:ring-2 ${
                              validationErrors.title
                                ? 'border-red-400 bg-red-500/10 focus:ring-red-400/30'
                                : 'border-white/20 bg-white/10 focus:border-transparent focus:ring-white/30'
                            }`}
                            placeholder="Enter title... *"
                          />
                          {validationErrors.title && (
                            <p className="mt-1 text-xs text-red-400">Title is required</p>
                          )}
                        </div>
                        <div className="flex space-x-1">
                          <button
                            onClick={saveChanges}
                            className="rounded-full bg-green-500/20 p-1 text-green-400 transition-colors duration-200 hover:bg-green-500/30 hover:text-green-300 disabled:cursor-not-allowed disabled:opacity-50"
                            title="Save (Ctrl+Enter)"
                            disabled={!editValues.title.trim() || !editValues.description.trim()}
                          >
                            <Check size={16} />
                          </button>
                          <button
                            onClick={cancelEditing}
                            className="rounded-full bg-red-500/20 p-1 text-red-400 transition-colors duration-200 hover:bg-red-500/30 hover:text-red-300"
                            title="Cancel (Esc)"
                          >
                            <X size={16} />
                          </button>
                        </div>
                      </div>
                      <div>
                        <textarea
                          ref={descriptionInputRef}
                          value={editValues.description}
                          onChange={(e) => handleInputChange('description', e.target.value)}
                          onKeyDown={handleKeyDown}
                          className={`w-full resize-none rounded-lg border px-3 py-2 text-white placeholder-white/50 transition-colors duration-200 focus:outline-none focus:ring-2 ${
                            validationErrors.description
                              ? 'border-red-400 bg-red-500/10 focus:ring-red-400/30'
                              : 'border-white/20 bg-white/10 focus:border-transparent focus:ring-white/30'
                          }`}
                          placeholder="Enter description... *"
                          rows={2}
                        />
                        {validationErrors.description && (
                          <p className="mt-1 text-xs text-red-400">Description is required</p>
                        )}
                      </div>
                    </div>
                  ) : (
                    // View Mode
                    <div
                      className="-m-2 cursor-pointer rounded-lg p-2 font-figtree text-base text-white transition-colors duration-200 hover:bg-white/5"
                      onClick={() => startEditing(e)}
                    >
                      <span className="font-semibold text-white/90">
                        {e.id}. {e.title || 'Untitled Section'}
                      </span>
                      <span className="ml-2 text-white/70">
                        {e.description || 'Click to add description...'}
                      </span>
                    </div>
                  )}
                </div>

                {/* Delete Button */}
                <DeleteOutlineSection
                  onDelete={() => {}}
                  trigger={
                    <div className="flex size-12 min-w-12 cursor-pointer items-center justify-center rounded-full bg-red-500/10 text-red-400 opacity-70 transition-all duration-200 hover:bg-red-500/20 hover:text-red-300 active:scale-95 group-hover:opacity-100">
                      <Trash2 size={18} />
                    </div>
                  }
                />
              </Card>
            ))
          : state.map((e) => (
              <Card
                key={e.id}
                className="group cursor-pointer border border-white/20 bg-white/10 backdrop-blur-sm transition-all duration-200 hover:bg-white/15 hover:shadow-lg hover:shadow-white/10"
                onClick={() => startEditing(e)}
              >
                <div className="p-4">
                  <div className="font-figtree text-base text-white">
                    <span className="font-semibold text-white/90 transition-colors duration-200 group-hover:text-white">
                      {e.id}. {e.title || 'Untitled Section'}
                    </span>
                    <span className="ml-2 text-white/70 transition-colors duration-200 group-hover:text-white/80">
                      {e.description || 'Click to add description...'}
                    </span>
                  </div>
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
          <Button className="w-full transition-colors duration-200 hover:bg-white/90 lg:w-fit">
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
              <Edit2 size={20} className="min-w-5" /> Edit Script
            </Button>
            <Button
              variant="gray"
              className="min-w-[166px] transition-colors duration-200 hover:bg-white/20"
            >
              <RefreshCcw size={20} className="min-w-5" /> Regenerate
            </Button>
          </Row>
          <Button className="w-full transition-colors duration-200 hover:bg-white/90 lg:w-fit">
            {directFileIcon} Download
          </Button>
        </Row>
      )}
    </>
  );
}
