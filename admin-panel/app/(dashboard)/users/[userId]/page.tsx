'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { CheckCircle, Trash2, User as UserIcon, XCircle } from 'lucide-react';

import { getClientDataAction } from 'lib/utils/clientDataActions';

type UserDetail = {
  id: number | string;
  fullname?: string | null;
  email?: string | null;
  date_joined?: string | null;
  is_active?: boolean;
  is_admin?: boolean;
  roles_display?: string[];
  last_login?: string | null;
  title_generation?: string;
  script?: string;
};

export default function UserDetailPageClient() {
  const router = useRouter();
  const params = useParams() as { userId: string };
  const userId = params?.userId;

  const [user, setUser] = useState<UserDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!userId) return;

    const fetchUser = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await getClientDataAction<{ data: UserDetail }>(`v1/admin/users/${userId}/`);
        const staticUser = {
          ...res?.data,
          title_generation: 'Top 10 AI Tools That Will Change Your Life',
          script:
            'This video explores the top 10 AI tools that are revolutionizing productivity and creativity. From design automation to writing assistants — discover how AI is shaping the future of work.',
        };
        setUser(staticUser);
      } catch (err: any) {
        console.error('Failed to fetch user detail:', err);
        setError(err?.message || 'Failed to fetch user');
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, [userId]);

  const formatDate = (d?: string | null) => (d ? new Date(d).toLocaleString() : '—');

  return (
    <div className="p-6">
      <div className="mx-auto max-w-full">
        <div className="rounded-2xl bg-gradient-to-r from-[#0f1112] to-[#161616] p-6 shadow-xl">
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <div className="h-12 w-12 animate-spin rounded-full border-4 border-white border-t-transparent" />
            </div>
          ) : error ? (
            <div className="rounded border border-red-500 bg-red-900/20 p-4">
              <div className="text-red-300">Error: {error}</div>
            </div>
          ) : user ? (
            <div className="grid grid-cols-1 gap-6 md:grid-cols-3 md:items-start">
              {/* Left: avatar, status, actions */}
              <div className="space-y-4">
                <div className="border-white/6 bg-white/3 rounded-xl border p-6 text-center">
                  <div className="bg-white/6 mx-auto mb-4 flex h-28 w-28 items-center justify-center overflow-hidden rounded-full text-4xl text-white">
                    {user.fullname ? user.fullname[0].toUpperCase() : <UserIcon />}
                  </div>

                  <div className="text-lg font-semibold text-white">
                    {user.fullname || 'No name'}
                  </div>
                  <div className="text-sm text-gray-300">{user.email}</div>

                  <div className="mt-5 flex flex-col items-center gap-3">
                    <div className="w-full">
                      {user.is_active ? (
                        <div className="inline-flex w-full items-center justify-center gap-2 rounded-full bg-green-800/25 px-3 py-2 text-sm font-semibold text-green-200">
                          <CheckCircle size={16} /> Active
                        </div>
                      ) : (
                        <div className="inline-flex w-full items-center justify-center gap-2 rounded-full bg-red-800/25 px-3 py-2 text-sm font-semibold text-red-200">
                          <XCircle size={16} /> Inactive
                        </div>
                      )}
                    </div>

                    <div className="flex w-full gap-3">
                      <button
                        onClick={() => console.log('toggle active')}
                        className="flex-1 rounded-md bg-yellow-700/30 px-3 py-2 text-sm font-medium text-yellow-50 hover:bg-yellow-700/40"
                      >
                        {user.is_active ? 'Deactivate' : 'Activate'}
                      </button>

                      <button
                        onClick={() => console.log('delete')}
                        className="rounded-md bg-red-700/30 px-3 py-2 text-sm font-medium text-red-50 hover:bg-red-700/40"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>
                </div>

                <div className="border-white/6 bg-white/3 rounded-xl border p-4">
                  <div className="text-sm text-gray-400">Roles</div>
                  <div className="mt-2 text-sm font-medium text-white">
                    {user.is_admin ? 'Admin' : user.roles_display?.join(', ') || 'User'}
                  </div>
                </div>
              </div>

              {/* Right: details + static fields */}
              <div className="md:col-span-2">
                <div className="border-white/6 bg-white/3 rounded-xl border p-6">
                  <div className="mb-4">
                    <h2 className="text-2xl font-bold text-white">User details</h2>
                    <p className="text-sm text-gray-400">Overview and activity for this user</p>
                  </div>

                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <DetailRow label="User ID" value={String(user.id)} />
                    <DetailRow label="Signup date" value={formatDate(user.date_joined)} />
                    <DetailRow label="Last login" value={formatDate(user.last_login)} />
                    <DetailRow label="Email" value={user.email || '—'} />
                  </div>

                  <div className="mt-6">
                    <h3 className="mb-2 text-lg font-semibold text-white">Recent activity</h3>
                    <div className="border-white/6 rounded-lg border bg-black/10 p-4 text-sm text-gray-300">
                      No recent activity available.
                    </div>
                  </div>
                </div>

                {/* Title Generation + Script (static text) */}
                <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-3">
                  <div className="border-white/6 bg-white/3 rounded-xl border p-4">
                    <div className="text-sm text-gray-400">Title generation</div>
                    <div className="mt-3 rounded-md bg-black/20 p-3 text-sm text-white">
                      {user.title_generation || 'No title available'}
                    </div>
                  </div>

                  <div className="border-white/6 bg-white/3 rounded-xl border p-4 md:col-span-2">
                    <div className="text-sm text-gray-400">Script</div>
                    <div className="mt-3 rounded-md bg-black/20 p-3 text-sm leading-relaxed text-gray-200">
                      {user.script ||
                        'No script data available. This will later show generated script text from API.'}
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-3">
                  <div className="border-white/6 bg-white/3 rounded-xl border p-4">
                    <div className="text-sm text-gray-400">Metadata</div>
                    <div className="mt-2 text-sm text-white">
                      Role: {user.is_admin ? 'Admin' : 'User'}
                    </div>
                  </div>

                  <div className="border-white/6 bg-white/3 rounded-xl border p-4 md:col-span-2">
                    <div className="text-sm text-gray-400">Actions</div>
                    <div className="mt-2 flex flex-wrap gap-2">
                      <button
                        onClick={() => navigator.clipboard.writeText(String(user.id))}
                        className="bg-white/6 rounded-md px-3 py-2 text-sm font-medium text-white hover:bg-white/10"
                      >
                        Copy ID
                      </button>

                      <button
                        onClick={() => router.push(`/admin/users/${user.id}/edit`)}
                        className="bg-white/6 rounded-md px-3 py-2 text-sm font-medium text-white hover:bg-white/10"
                      >
                        Edit user
                      </button>

                      <button
                        onClick={() => console.log('Open permissions')}
                        className="bg-white/6 rounded-md px-3 py-2 text-sm font-medium text-white hover:bg-white/10"
                      >
                        Manage permissions
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-gray-300">No user data</div>
          )}
        </div>
      </div>
    </div>
  );
}

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-1">
      <div className="text-xs text-gray-400">{label}</div>
      <div className="text-sm font-medium text-white">{value}</div>
    </div>
  );
}
