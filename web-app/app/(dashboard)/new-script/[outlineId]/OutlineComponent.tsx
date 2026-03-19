'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  ArrowLeft,
  FileText,
  Lightbulb,
  Megaphone,
  Mic,
  Pencil,
  PlusCircle,
  RefreshCcw,
  Tags,
} from 'lucide-react';

import { LoadingScreen } from '../_components/components';
import { FormType, OutlineType } from '../types';
import { CardView } from './_components/CardView';
import { SortableCard } from './_components/SortableCard';
import { useCardManager } from './_components/useCardManager';
import { useDragAndDrop } from './_components/useDragAndDrop';
import useGenerateOutline from 'lib/hooks/useGenerateOutline';
import useGenerateScript from 'lib/hooks/useGenerateScript';
import useUpdateOutline from 'lib/hooks/useUpdateOutline';
import useUpdateOutlineOrder from 'lib/hooks/useUpdateOutlineOrder';
import { logger } from 'lib/logger';
import useToast from 'lib/utils/useToast';
import { Button } from 'components/ui/Button';
import { Spinner } from 'components/ui/Spinner';

// ── Helpers ───────────────────────────────────────────────────────────────────

const convertOutlineToCards = (outline: OutlineType) => {
  if (!outline?.outline_data?.sections) return [];
  const sectionOrder = outline.section_order || outline.outline_data.sections.map((_, i) => i);
  return sectionOrder
    .map((index) => outline.outline_data.sections[index])
    .filter(Boolean)
    .map((section, index) => ({
      id: index + 1,
      title: section.title || '',
      description: section.description || '',
      keyPoints: section.key_points || [],
      timing: section.timing || '',
      transition: section.transition || '',
    }));
};

const convertCardsToOutline = (cards: any[], originalOutline: OutlineType) => ({
  ...originalOutline,
  outline_data: {
    ...originalOutline.outline_data,
    sections: cards.map((card) => ({
      title: card.title || '',
      description: card.description || '',
      key_points: card.keyPoints || [],
      timing: card.timing || '',
      transition: card.transition || '',
    })),
  },
});

// ── Component ─────────────────────────────────────────────────────────────────

export default function OutlineComponent({ outline }: { outline: OutlineType }) {
  const toast = useToast();
  const router = useRouter();
  const [edit, setEdit] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  const { isPending: isSaving, mutate: updateOutline } = useUpdateOutline();
  const { isPending: isUpdatingOrder, mutate: updateOutlineOrder } = useUpdateOutlineOrder();
  const { isPending: isGeneratingScript, mutate: generateScript } = useGenerateScript();
  const { isPending: isRegeneratingOutline, mutate: generateOutline } = useGenerateOutline();

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const initialCards = outline ? convertOutlineToCards(outline) : [];

  // ── Delete ────────────────────────────────────────────────────────────────
  const handleDelete = (cardId: number) => {
    if (!outline) return;
    const cardIndex = cards.findIndex((c) => c.id === cardId);
    const newCards = cards.filter((c) => c.id !== cardId);
    setCards(newCards);

    const newSectionOrder = [...(outline.section_order || [])];
    if (cardIndex < newSectionOrder.length) newSectionOrder.splice(cardIndex, 1);

    updateOutlineOrder(
      {
        uuid: outline.id,
        sectionOrder: newSectionOrder,
        outlineData: convertCardsToOutline(newCards, outline).outline_data,
      },
      {
        onSuccess: () => toast.success('Success', 'Section deleted'),
        onError: (error) => {
          logger.error(error);
          toast.error('Something went wrong', 'Error deleting section');
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

  const { handleDragStart, handleDragOver, handleDragLeave, handleDrop, handleDragEnd } =
    useDragAndDrop(cards, setCards, draggedCard, setDraggedCard, dragOverIndex, setDragOverIndex);

  // Track changes
  useEffect(() => {
    setHasChanges(JSON.stringify(cards) !== JSON.stringify(initialCards));
  }, [cards, initialCards]);

  // ── Save ──────────────────────────────────────────────────────────────────
  const handleSaveChanges = () => {
    if (!outline) return;
    const invalid = cards.find((c) => !c.title?.trim() || !c.description?.trim());
    if (invalid) {
      toast.error('Missing Fields', 'Every section must have a title and description.');
      return;
    }
    updateOutline(convertCardsToOutline(cards, outline), {
      onSuccess: () => {
        toast.success('Success', 'Outline updated');
        setHasChanges(false);
        setEdit(false);
      },
      onError: (error) => {
        logger.error(error);
        toast.error('Something went wrong', 'Error updating outline');
      },
    });
  };

  // ── Regenerate ────────────────────────────────────────────────────────────
  const handleRegenerate = async () => {
    if (!outline) return;

    let savedRaw: string | null = null;
    try {
      savedRaw =
        typeof window !== 'undefined' ? localStorage.getItem('last_outline_payload') : null;
    } catch (e) {
      logger.warn('Could not read last_outline_payload', e);
    }

    let payloadToSend: any = null;

    if (savedRaw) {
      try {
        const saved = JSON.parse(savedRaw);
        if (saved?.hasImageFile && saved?.data) {
          const fd = new FormData();
          fd.append('description', saved.data.description ?? '');
          (saved.data.tones || []).forEach((t: any) => fd.append('tones', String(t)));
          if (saved.data.template_style)
            fd.append('template_style', String(saved.data.template_style));
          else {
            fd.append('min_length', String(saved.data.min_length ?? 0));
            fd.append('max_length', String(saved.data.max_length ?? 500));
          }
          fd.append('title', String(saved.data.title ?? ''));
          if (saved.data.niche_id) fd.append('niche_id', String(saved.data.niche_id));
          (saved.data.linkItems || []).forEach((l: string) => fd.append('youtube_url', l));
          (saved.data.articleItems || []).forEach((a: string) => fd.append('article_url', a));
          for (const img of saved.data.images || []) {
            try {
              const res = await fetch(img.dataUrl);
              const blob = await res.blob();
              fd.append(
                'image',
                new File([blob], img.name || 'image', { type: img.type || blob.type }),
              );
            } catch (err) {
              logger.warn('Failed to reconstruct image', err);
            }
          }
          payloadToSend = fd;
        } else if (saved?.hasImageFile === false && saved?.payload) {
          payloadToSend = saved.payload;
        }
      } catch (e) {
        logger.warn('Could not parse saved payload', e);
      }
    }

    if (!payloadToSend) {
      const payload: Partial<FormType> = {
        description: outline.description || '',
        tones: outline.tones ? outline.tones.map((t: any) => t.id) : [],
        template_style: outline.template_style ?? undefined,
        min_length: outline.min_length || 0,
        max_length: outline.max_length || 500,
        title: outline.title || '',
      };
      try {
        const saved = localStorage.getItem('draft_description');
        if (saved?.trim()) payload.description = saved;
      } catch (e) {
        logger.warn('Could not read draft_description', e);
      }
      payloadToSend = payload;
    }

    generateOutline(payloadToSend, {
      onSuccess: (data) => {
        toast.success('Success', 'Outline regenerated');
        router.replace(`/new-script/${data.outline.id}`);
      },
      onError: (error) => {
        logger.error(error);
        toast.error('Something went wrong', 'Error regenerating outline');
      },
    });
  };

  // ── Generate script ───────────────────────────────────────────────────────
  const handleGenerateScript = () => {
    if (!outline) return;
    generateScript(outline.id, {
      onSuccess: (data) => {
        toast.success('Success', 'Script generated');
        router.replace(`/new-script/script/${data.script.id}`);
      },
      onError: (error) => {
        logger.error(error);
        toast.error('Something went wrong', 'Error generating script');
      },
    });
  };

  if (!outline) {
    return (
      <div className="flex h-64 items-center justify-center">
        <p className="text-sm text-muted-foreground">Loading outline…</p>
      </div>
    );
  }

  const isBusy = isRegeneratingOutline || isGeneratingScript;
  const toneNames = Array.isArray(outline.tones)
    ? outline.tones.map((t: any) => (typeof t === 'object' ? t.name : String(t))).join(', ')
    : '';
  // ── Render ────────────────────────────────────────────────────────────────
  if (isBusy) return <LoadingScreen />;

  return (
    <div className="flex flex-col gap-6">
      {/* Saving overlay */}
      {(isSaving || isUpdatingOrder) && (
        <div className="flex items-center gap-2 rounded-lg border border-border bg-accent px-3 py-2">
          <Spinner size="sm" color="primary" />
          <span className="text-xs text-muted-foreground">Saving changes…</span>
        </div>
      )}

      {/* ── Status row ── */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="flex flex-col gap-1.5 rounded-lg border border-border bg-card p-4 sm:p-5">
          <p className="text-[13px] font-medium text-muted-foreground">Topic</p>
          <p className="line-clamp-1 text-[18px] font-semibold leading-tight tracking-tight text-foreground sm:text-[22px]">
            {outline.title || 'Untitled'}
          </p>
          <p className="line-clamp-2 text-[13px] font-medium leading-relaxed text-muted-foreground">
            {outline.description || 'No description provided.'}
          </p>
        </div>
        <div className="flex flex-col gap-1.5 rounded-lg border border-border bg-card p-4 sm:p-5">
          <p className="text-[13px] font-medium text-muted-foreground">Tone</p>
          <p className="line-clamp-1 text-[18px] font-semibold leading-tight tracking-tight text-foreground sm:text-[22px]">
            {toneNames || 'Default'}
          </p>
          <p className="text-[13px] font-medium leading-relaxed text-muted-foreground">
            A creator-friendly structure with crisp transitions and practical examples.
          </p>
        </div>
        <div className="flex flex-col gap-1.5 rounded-lg border border-border bg-card p-4 sm:p-5">
          <p className="text-[13px] font-medium text-muted-foreground">Estimated runtime</p>
          <p className="text-[18px] font-semibold leading-tight tracking-tight text-foreground sm:text-[22px]">
            {Math.round((outline.min_length || outline.max_length || 1000) / 130)}–
            {Math.round((outline.max_length || 1000) / 100)} min
          </p>
          <p className="text-[13px] font-medium leading-relaxed text-muted-foreground">
            Balanced pacing across {cards.length} sections with a strong closing CTA.
          </p>
        </div>
      </div>

      {/* ── Main 2-column grid ── */}
      <div className="grid gap-6 lg:grid-cols-[minmax(0,1.45fr)_minmax(300px,0.8fr)]">
        {/* ── Outline panel ── */}
        <div className="flex flex-col gap-6 rounded-lg border border-border bg-card p-4 sm:p-6">
          {/* Header */}
          <div className="flex items-start gap-4">
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-start justify-between gap-2">
                <h2 className="text-[18px] font-semibold tracking-tight text-foreground sm:text-[20px]">
                  Generated outline
                </h2>
                <span className="shrink-0 rounded-full bg-secondary px-3 py-1.5 text-xs font-semibold text-secondary-foreground">
                  {cards.length} sections
                </span>
              </div>
              <p className="mt-1 text-sm font-medium text-muted-foreground">
                Each section is optimized for YouTube flow, watch time, and creator-friendly
                delivery.
              </p>
            </div>
          </div>

          {/* Sections list */}
          <div className="flex flex-col gap-3">
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
              : cards.map((card, index) => (
                  <div
                    key={card.id}
                    className="flex items-start gap-3.5 rounded-md bg-secondary p-4"
                  >
                    <div className="flex h-[30px] w-[30px] shrink-0 items-center justify-center rounded-full bg-card text-[13px] font-semibold text-foreground">
                      {index + 1}
                    </div>
                    <div className="min-w-0 flex-1">
                      <CardView card={card} onEdit={startEditing} />
                    </div>
                  </div>
                ))}
          </div>

          {/* Actions */}
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            {edit ? (
              <>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" onClick={() => setEdit(false)}>
                    <ArrowLeft className="h-4 w-4" /> Back
                  </Button>
                  <Button variant="outline" size="sm" onClick={addNewCard}>
                    <PlusCircle className="h-4 w-4" /> Add section
                  </Button>
                </div>
                <Button
                  size="sm"
                  onClick={handleSaveChanges}
                  loading={isSaving}
                  disabled={!hasChanges}
                >
                  Save changes
                </Button>
              </>
            ) : (
              <>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" onClick={() => setEdit(true)}>
                    <Pencil className="h-4 w-4" /> Edit outline
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleRegenerate}
                    loading={isRegeneratingOutline}
                  >
                    <RefreshCcw className="h-4 w-4" /> Regenerate
                  </Button>
                </div>
                <Button size="sm" onClick={handleGenerateScript} loading={isGeneratingScript}>
                  <FileText className="h-4 w-4" /> Generate full script
                </Button>
              </>
            )}
          </div>
        </div>

        {/* ── Insights panel ── */}
        <div className="flex flex-col gap-5 rounded-lg border border-border bg-card p-4 sm:p-6">
          <div>
            <div className="flex flex-wrap items-start justify-between gap-2">
              <h2 className="text-[18px] font-semibold tracking-tight text-foreground sm:text-[20px]">
                Outline insights
              </h2>
              <span className="shrink-0 rounded-full bg-secondary px-3 py-1.5 text-xs font-semibold text-secondary-foreground">
                Ready
              </span>
            </div>
            <p className="mt-1 text-sm font-medium text-muted-foreground">
              Quick checks before you move into the long-form draft.
            </p>
          </div>

          <div className="flex flex-col gap-4">
            {/* Hook strength */}
            <div className="flex flex-col gap-2 rounded-md bg-secondary p-4">
              <div className="flex items-center gap-2">
                <Lightbulb className="h-4 w-4 shrink-0 text-muted-foreground" />
                <p className="text-sm font-semibold text-foreground">Hook strength</p>
              </div>
              <p className="text-sm font-medium leading-relaxed text-muted-foreground">
                Strong opening concept with broad appeal. Add one surprising stat or bold promise to
                improve first-30-second retention.
              </p>
            </div>

            {/* Audience fit */}
            <div className="flex flex-col gap-3 rounded-md bg-secondary p-4">
              <div className="flex items-center gap-2">
                <Tags className="h-4 w-4 shrink-0 text-muted-foreground" />
                <p className="text-sm font-semibold text-foreground">Audience fit</p>
              </div>
              <div className="flex flex-wrap gap-2">
                {['Productivity', 'Self-improvement', 'Creator economy'].map((tag) => (
                  <span
                    key={tag}
                    className="rounded-full bg-card px-3 py-1.5 text-xs font-semibold text-foreground"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>

            {/* Delivery notes */}
            <div className="flex flex-col gap-2 rounded-md bg-secondary p-4">
              <div className="flex items-center gap-2">
                <Mic className="h-4 w-4 shrink-0 text-muted-foreground" />
                <p className="text-sm font-semibold text-foreground">Delivery notes</p>
              </div>
              <p className="text-sm font-medium leading-relaxed text-muted-foreground">
                Keep examples short, transition quickly between sections, and reinforce one key
                result after every beat.
              </p>
            </div>

            {/* Suggested CTA */}
            <div className="flex flex-col gap-2 rounded-md bg-secondary p-4">
              <div className="flex items-center gap-2">
                <Megaphone className="h-4 w-4 shrink-0 text-muted-foreground" />
                <p className="text-sm font-semibold text-foreground">Suggested CTA</p>
              </div>
              <p className="text-sm font-medium leading-relaxed text-muted-foreground">
                Ask viewers which section resonated most, then invite them to subscribe for more
                practical creator workflows.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
