'use client';

import { CheckCircle, Eye, Trash2, User as UserIcon, XCircle } from 'lucide-react';
import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

import { useAdminUsers } from 'lib/api/hooks';
import { getClientDataAction } from 'lib/utils/clientDataActions';
import { toast } from 'sonner';

type ScriptRow = {
  id: string | number;
  content: string;
};

type UserDetail = {
  id: number | string;
  fullname?: string | null;
  email?: string | null;
  date_joined?: string | null;
  is_active?: boolean;
  is_admin?: boolean;
  roles_display?: string[];
  last_login?: string | null;
  titles?: string[];
  scripts?: ScriptRow[];
};

export default function UserDetailPageClient() {
  const router = useRouter();
  const params = useParams() as { userId: string };
  const userId = params?.userId;

  const [user, setUser] = useState<UserDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // UI state for viewing a script
  const [selectedScript, setSelectedScript] = useState<ScriptRow | null>(null);

  const { activateUser, deactivateUser, deleteUser } = useAdminUsers();

  const handleActivateUser = async (id: string) => {
    try {
      await activateUser(id);
      setUser((prev) => (prev ? { ...prev, is_active: true } : prev));
      toast.success('User activated successfully');
    } catch (error) {
      console.error('Failed to activate user:', error);
      toast.error('Failed to activate user');
    }
  };

  const handleDeactivateUser = async (id: string) => {
    try {
      await deactivateUser(id);
      setUser((prev) => (prev ? { ...prev, is_active: false } : prev));
      toast.success('User deactivated successfully');
    } catch (error) {
      console.error('Failed to deactivate user:', error);
      toast.error('Failed to deactivate user');
    }
  };

  const handleDeleteUser = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      try {
        await deleteUser(id);
        toast.success('User deleted successfully');
        router.push('/users');
      } catch (error) {
        console.error('Failed to delete user:', error);
        toast.error('Failed to delete user');
      }
    }
  };

  useEffect(() => {
    if (!userId) return;

    const fetchUser = async () => {
      setLoading(true);
      setError(null);
      try {
        // fetch user; we're adding static arrays for titles and scripts for now
        const res = await getClientDataAction<{ data: UserDetail }>(`v1/admin/users/${userId}/`);
        const staticUser: UserDetail = {
          ...res?.data,
          titles: [
            'Top 10 AI Tools That Will Change Your Life',
            'How To Use AI To Double Your Productivity',
            'The Future of Creative Work with AI',
          ],
          scripts: [
            {
              id: 1,
              content:
                'This video explores the top 10 AI tools that are revolutionizing productivity and creativity. From design automation to writing assistants — discover how AI is shaping the future of work.',
            },
            {
              id: 2,
              content:
                "In this short guide we'll walk through practical workflows to integrate AI into your daily tasks so you can save time and focus on higher-value work.",
            },
          ],
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

  const copyText = async (text: string | undefined) => {
    if (!text) return;
    try {
      await navigator.clipboard.writeText(text);
      // subtle feedback — you can replace with toast if you have one
      // For now we'll just use console.log (or you can import your toast util)
      console.log('Copied to clipboard');
    } catch {
      console.warn('Clipboard write failed');
    }
  };

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
                        onClick={() =>
                          user.is_active
                            ? handleDeactivateUser(String(user.id))
                            : handleActivateUser(String(user.id))
                        }
                        className="flex-1 rounded-md bg-yellow-700/30 px-3 py-2 text-sm font-medium text-yellow-50 hover:bg-yellow-700/40"
                      >
                        {user.is_active ? 'Deactivate' : 'Activate'}
                      </button>

                      <button
                        onClick={() => handleDeleteUser(String(user.id))}
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

              {/* Right: details + tables */}
              <div className="space-y-6 md:col-span-2">
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
                </div>

                {/* Titles table */}
                <div className="border-white/6 bg-white/3 rounded-xl border p-4">
                  <div className="mb-3 flex items-center justify-between">
                    <h3 className="text-lg font-semibold text-white">Titles</h3>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full table-auto text-sm">
                      <thead>
                        <tr className="text-left text-xs text-gray-400">
                          <th className="px-3 py-2">#</th>
                          <th className="px-3 py-2">Title</th>
                          <th className="px-3 py-2">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(user.titles ?? []).map((t, i) => (
                          <tr key={i} className="border-white/6 border-t">
                            <td className="px-3 py-3 text-gray-300">{i + 1}</td>
                            <td className="px-3 py-3 text-white">{t}</td>
                            <td className="px-3 py-3">
                              <div className="flex gap-2">
                                <button
                                  onClick={() => copyText(t)}
                                  className="bg-white/6 rounded-md px-2 py-1 text-xs text-white hover:bg-white/10"
                                >
                                  Copy
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                        {(user.titles ?? []).length === 0 && (
                          <tr>
                            <td colSpan={3} className="px-3 py-6 text-center text-sm text-gray-400">
                              No titles available.
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Scripts table */}
                <div className="border-white/6 bg-white/3 rounded-xl border p-4">
                  <div className="mb-3 flex items-center justify-between">
                    <h3 className="text-lg font-semibold text-white">Scripts</h3>
                  </div>

                  <div className="overflow-hidden">
                    {' '}
                    <table className="w-full table-auto text-sm">
                      <thead>
                        <tr className="text-left text-xs text-gray-400">
                          <th className="w-10 px-3 py-2">#</th>
                          <th className="px-3 py-2">Preview</th>
                          <th className="w-32 px-3 py-2">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(user.scripts ?? []).map((s, i) => (
                          <tr key={s.id} className="border-white/6 border-t align-top">
                            <td className="px-3 py-3 text-gray-300">{i + 1}</td>
                            <td className="px-3 py-3 text-white">
                              <div className="whitespace-normal break-words">{s.content}</div>
                            </td>
                            <td className="px-3 py-3">
                              <div className="flex gap-2">
                                <button
                                  onClick={() => setSelectedScript(s)}
                                  className="bg-white/6 inline-flex items-center gap-2 rounded-md px-2 py-1 text-xs text-white hover:bg-white/10"
                                >
                                  <Eye size={14} /> View
                                </button>
                                <button
                                  onClick={() => copyText(s.content)}
                                  className="bg-white/6 rounded-md px-2 py-1 text-xs text-white hover:bg-white/10"
                                >
                                  Copy
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}

                        {(user.scripts ?? []).length === 0 && (
                          <tr>
                            <td colSpan={3} className="px-3 py-6 text-center text-sm text-gray-400">
                              No scripts available.
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>

                  {/* Inline script viewer */}
                  {selectedScript && (
                    <div className="border-white/6 mt-4 rounded-md border bg-black/10 p-4">
                      <div className="flex items-start justify-between gap-4">
                        <div className="text-sm font-semibold text-white">
                          Script #{selectedScript.id}
                        </div>
                        <button
                          onClick={() => setSelectedScript(null)}
                          className="text-sm text-gray-400 hover:text-white"
                        >
                          Close
                        </button>
                      </div>
                      <div className="mt-2 whitespace-pre-wrap text-sm leading-relaxed text-gray-200">
                        {selectedScript.content}
                      </div>
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="mt-2 grid grid-cols-1 gap-4 md:grid-cols-3">
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
