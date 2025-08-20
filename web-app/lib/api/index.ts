import { env } from '../../env.mjs';

// request methods
export const method = {
  post: 'POST',
  get: 'GET',
  delete: 'DELETE',
  put: 'PUT',
  patch: 'PATCH',
};

// main or branch
export const baseUrl = env.NEXT_PUBLIC_API_URL;
