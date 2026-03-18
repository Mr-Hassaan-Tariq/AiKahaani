'use client';

import { Dispatch, ReactNode, SetStateAction } from 'react';
import { DialogTrigger } from '@radix-ui/react-dialog';

import { cn } from 'lib/utils';
import {
  DialogClose,
  DialogContent,
  DialogFooter,
  Dialog as ShadcnDialog,
} from 'components/shadcn_ui/dialog';

export default function Dialog({
  trigger,
  title,
  description,
  closeActionButton,
  footer,
  open,
  setOpen,
  children,
  className,
  overlayClasses,
  outsideInteract = true,
}: DialogProps) {
  return (
    <ShadcnDialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent
        className={cn(
          'scrollbar max-h-[90dvh] overflow-y-auto rounded-2xl border border-border bg-card px-6 py-8 shadow-md sm:max-w-[480px] sm:rounded-2xl sm:px-8',
          className,
        )}
        overlayClasses={cn('bg-foreground/20 backdrop-blur-sm', overlayClasses)}
        onInteractOutside={(event) => !outsideInteract && event.preventDefault()}
      >
        <div className="flex flex-col gap-3">
          {title && <h2 className="text-center text-lg font-semibold text-foreground">{title}</h2>}
          {description && (
            <p
              className="text-center text-sm leading-relaxed text-muted-foreground"
              dangerouslySetInnerHTML={
                typeof description === 'string' ? { __html: description } : undefined
              }
            >
              {typeof description !== 'string' ? description : null}
            </p>
          )}
        </div>

        {children && <div className="mt-4">{children}</div>}

        <DialogFooter className="mt-6">
          {footer}
          {closeActionButton && (
            <DialogClose asChild className="w-full">
              {closeActionButton}
            </DialogClose>
          )}
        </DialogFooter>
      </DialogContent>
    </ShadcnDialog>
  );
}

type DialogProps = {
  trigger: ReactNode;
  title?: string | ReactNode;
  description?: ReactNode | string;
  closeActionButton?: ReactNode;
  footer?: ReactNode;
  open?: boolean;
  setOpen?: Dispatch<SetStateAction<boolean>>;
  children?: ReactNode;
  className?: string;
  outsideInteract?: boolean;
  overlayClasses?: string;
};
