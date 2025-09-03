'use client';

import { Dispatch, ReactNode, SetStateAction } from 'react';
import { DialogTrigger } from '@radix-ui/react-dialog';

import Col from './Col';
import Text from './Text';
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
          'sm:py-12" scrollbar max-h-[95dvh] overflow-y-auto rounded-3xl border-[#BAFF38]/30 bg-brand-surface px-4 py-8 text-white shadow-[0_45px_103px_0_rgba(255,255,255,0.04),0_9px_16.737px_0_rgba(255,255,255,0.02)] sm:max-w-[640px] sm:rounded-3xl sm:px-12',
          className,
        )}
        overlayClasses={overlayClasses}
        onInteractOutside={(event) => !outsideInteract && event.preventDefault()}
      >
        <Col className="gap-4">
          <Text variant="3xl" className="w-full text-center font-semibold text-white">
            {title}
          </Text>
          {description && (
            <Text variant="lg" className="text-center text-[#AAACA6]">
              {description}
            </Text>
          )}
        </Col>
        <div className="flex flex-col items-center justify-center">{children}</div>
        <DialogFooter>
          {footer}
          <DialogClose asChild className="w-full">
            {closeActionButton}
          </DialogClose>
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
