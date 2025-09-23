'use client';

import { useRouter } from 'next/navigation';
import { useMutation } from '@tanstack/react-query';

import { logger } from 'lib/logger';
import { deleteClientDataAction } from 'lib/utils/clientDataActions';
import useToast from 'lib/utils/useToast';

async function deleteScriptGeneration(uuid: string) {
  const res = await deleteClientDataAction<{ status: number }>(`v1/scripts/outlines/${uuid}/`);

  if (res.status === 204 || res.status === 200) {
    // Debug: Script deleted successfully
    // Example: logger.info('Script deleted successfully');
    return { success: true };
  }

  if (res.status === 404) {
    // Debug: Script not found
    // Example: logger.error('Script not found');
    throw new Error('Script not found');
  }

  // Debug: Unexpected status code
  // Example: logger.error(`Unexpected status code: ${res.status}`);
  throw new Error(`Unexpected status code: ${res.status}`);
}

async function deleteOutlineGeneration(uuid: string) {
  const res = await deleteClientDataAction<{ status: number }>(`v1/scripts/${uuid}/`);

  if (res.status === 204 || res.status === 200) {
    // Debug: Script deleted successfully
    // Example: logger.info('Script deleted successfully');
    return { success: true };
  }

  if (res.status === 404) {
    // Debug: Script not found
    // Example: logger.error('Script not found');
    throw new Error('Script not found');
  }

  // Debug: Unexpected status code
  // Example: logger.error(`Unexpected status code: ${res.status}`);
  throw new Error(`Unexpected status code: ${res.status}`);
}

export default function useDeleteScriptGeneration() {
  const toast = useToast();
  const router = useRouter();

  return useMutation({
    mutationFn: deleteScriptGeneration,
    onSuccess: () => {
      toast.success('Success', 'Script deleted successfully');
      router.refresh();
    },
    onError: (error: { detail: string }) => {
      logger.error(error);
      toast.error('Something went wrong', error.detail?.toString() || 'Failed to delete script');
    },
  });
}
export function useDeleteOutlineGeneration() {
  const toast = useToast();
  const router = useRouter();

  return useMutation({
    mutationFn: deleteOutlineGeneration,
    onSuccess: () => {
      toast.success('Success', 'Script deleted successfully');
      router.refresh();
    },
    onError: (error: { detail: string }) => {
      logger.error(error);
      toast.error('Something went wrong', error.detail?.toString() || 'Failed to delete script');
    },
  });
}
