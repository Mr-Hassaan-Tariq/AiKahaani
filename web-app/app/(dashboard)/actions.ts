'use server';

import { UserProfileType } from './types';
import { getServerDataAction } from 'lib/utils/getServerDataAction';

export async function getUserProfile() {
  return await getServerDataAction<UserProfileType>('v1/users/details/');
}
