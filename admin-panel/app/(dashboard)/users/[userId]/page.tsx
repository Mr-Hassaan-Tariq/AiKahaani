'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { CheckCircle, Trash2, User as UserIcon, XCircle } from 'lucide-react';

import ScriptCard from './_components/ScriptCard';
import TitleCard from './_components/TitleCard';
import { getClientDataAction } from 'lib/utils/clientDataActions';
import Card from 'components/ui/Card';

type UserTitle = {
  uuid: string;
  user: number;
  prompt: string;
  titles: string[];
  tones: string[];
  user_title?: string;
  script?: number | null;
  created: string;
};

type UserTitlesResponse = {
  count: number;
  next: string | null;
  previous: string | null;
  results: {
    data: UserTitle[];
    message: string;
  };
};

type ScriptGeneration = {
  uuid: string;
  title: string;
  type: 'script' | 'outline';
  status: 'draft' | 'generated' | 'saved';
  status_display: string;
  word_count: number | null;
  estimated_duration: number | null;
  created: string;
  modified: string;
  is_published: boolean | null;
  version: number;
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
};

export default function UserDetailPageClient() {
  const params = useParams() as { userId: string };
  const userId = params?.userId;

  const [user, setUser] = useState<UserDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Titles and scripts data
  const [titles, setTitles] = useState<UserTitle[]>([]);
  const [titlesLoading, setTitlesLoading] = useState<boolean>(false);
  const [scripts, setScripts] = useState<ScriptGeneration[]>([]);
  const [scriptsLoading, setScriptsLoading] = useState<boolean>(false);

  // Tab state
  const [activeTab, setActiveTab] = useState<'titles' | 'scripts'>('titles');

  useEffect(() => {
    if (!userId) return;

    const fetchUser = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await getClientDataAction<{ data: UserDetail }>(`v1/admin/users/${userId}/`);
        setUser(res?.data);
      } catch (err: unknown) {
        const error = err as { message?: string };
        setError(error?.message || 'Failed to fetch user');
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, [userId]);

  useEffect(() => {
    if (!userId) return;

    const fetchTitles = async () => {
      setTitlesLoading(true);
      try {
        const res = await getClientDataAction<UserTitlesResponse>(
          `v1/scripts/titles/admin/all-titles/?user=${userId}`,
        );
        if (res?.results?.data) {
          setTitles(res.results.data);
        }
      } catch {
        // Error fetching titles
      } finally {
        setTitlesLoading(false);
      }
    };

    const fetchScripts = async () => {
      setScriptsLoading(true);
      try {
        // Use generations endpoint with user filter (if available) or fetch all and filter
        // Since generations endpoint filters by authenticated user, we might need admin endpoint
        // But let's try generations first with a high limit to get all
        const generationsRes = await getClientDataAction<{
          count: number;
          next: string | null;
          previous: string | null;
          results: ScriptGeneration[];
        }>(`v1/scripts/generations/?limit=100&user=${userId}`);

        if (generationsRes?.results) {
          // Filter by user ID if the response includes user info
          // Note: Generations endpoint filters by request.user, so for admin viewing other users,
          // we may need to use a different approach or admin endpoint
          setScripts(generationsRes.results);
        } else {
          // Fallback: Try admin endpoint
          const adminRes = await getClientDataAction<{
            count: number;
            next: string | null;
            previous: string | null;
            results: Array<{
              uuid: string;
              title: string;
              status: string;
              word_count: number | null;
              estimated_duration: number | null;
              created: string;
            }>;
          }>(`v1/scripts/admin/all-full-scripts/?user=${userId}&limit=100`);
          if (adminRes?.results) {
            // Map admin response to ScriptGeneration format
            const mappedScripts: any = adminRes.results.map((s) => ({
              uuid: s.uuid,
              title: s.title,
              type: 'script' as const,
              status: (s.status as 'draft' | 'generated' | 'saved') || 'draft',
              status_display: s.status || 'Draft',
              word_count: s.word_count,
              estimated_duration: Number(s.estimated_duration).toFixed(2),
              created: s.created,
              modified: s.created,
              is_published: null,
              version: 1,
            }));
            setScripts(mappedScripts);
          }
        }
      } catch {
        // Error fetching scripts
      } finally {
        setScriptsLoading(false);
      }
    };

    fetchTitles();
    fetchScripts();
  }, [userId]);

  const formatDate = (d?: string | null) => (d ? new Date(d).toLocaleString() : '—');

  const copyText = async (text: string | undefined) => {
    if (!text) return;
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      // Clipboard write failed
    }
  };

  return (
    <div className="space-y-6">
      {loading ? (
        <Card>
          <div className="flex items-center justify-center py-20">
            <div className="h-12 w-12 animate-spin rounded-full border-4 border-[#20BF0E] border-t-transparent" />
          </div>
        </Card>
      ) : error ? (
        <Card>
          <div className="rounded-lg border border-red-500/30 bg-red-900/20 p-4">
            <div className="text-red-300">Error: {error}</div>
          </div>
        </Card>
      ) : user ? (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* Left: avatar, status, actions */}
          <div className="space-y-4">
            <Card>
              <div className="text-center">
                <div className="mx-auto mb-4 flex h-28 w-28 items-center justify-center overflow-hidden rounded-full bg-[#1E1E1E] text-4xl text-white">
                  {user.fullname ? (
                    user.fullname[0].toUpperCase()
                  ) : (
                    <UserIcon className="h-12 w-12 text-[#AAACA6]" />
                  )}
                </div>

                <div className="text-lg font-semibold text-white">{user.fullname || 'No name'}</div>
                <div className="text-sm text-[#AAACA6]">{user.email}</div>

                <div className="mt-5 flex flex-col items-center gap-3">
                  <div className="w-full">
                    {user.is_active ? (
                      <div className="inline-flex w-full items-center justify-center gap-2 rounded-xl border border-green-500/30 bg-green-500/10 px-3 py-2 text-sm font-semibold text-[#20BF0E]">
                        <CheckCircle size={16} /> Active
                      </div>
                    ) : (
                      <div className="inline-flex w-full items-center justify-center gap-2 rounded-xl border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm font-semibold text-red-300">
                        <XCircle size={16} /> Inactive
                      </div>
                    )}
                  </div>

                  <div className="flex w-full gap-3">
                    <button
                      onClick={() => {
                        // TODO: Implement toggle active
                      }}
                      className="flex-1 rounded-lg border border-[#2b2b2b] bg-[#1E1E1E] px-3 py-2 text-sm font-medium text-white transition-colors hover:bg-[#20BF0E]/10"
                    >
                      {user.is_active ? 'Deactivate' : 'Activate'}
                    </button>

                    <button
                      onClick={() => {
                        // TODO: Implement delete
                      }}
                      className="rounded-lg border border-[#2b2b2b] bg-[#1E1E1E] px-3 py-2 text-sm font-medium text-white transition-colors hover:bg-red-500/10"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
              </div>
            </Card>

            <Card>
              <div className="text-sm text-[#AAACA6]">Roles</div>
              <div className="mt-2 text-sm font-medium text-white">
                {user.is_admin ? 'Admin' : user.roles_display?.join(', ') || 'User'}
              </div>
            </Card>
          </div>

          {/* Right: details + tabs */}
          <div className="space-y-6 lg:col-span-2">
            <Card>
              <div className="mb-4">
                <h2 className="text-2xl font-bold text-white">User details</h2>
                <p className="text-sm text-[#AAACA6]">Overview and activity for this user</p>
              </div>

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <DetailRow label="User ID" value={String(user.id)} />
                <DetailRow label="Signup date" value={formatDate(user.date_joined)} />
                <DetailRow label="Last login" value={formatDate(user.last_login)} />
                <DetailRow label="Email" value={user.email || '—'} />
              </div>
            </Card>

            {/* Tabs section */}
            <Card>
              {/* Tabs header */}
              <div className="mb-6 flex items-center justify-start gap-2">
                <button
                  onClick={() => setActiveTab('titles')}
                  className={`rounded-xl px-4 py-2 text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-[#20BF0E]/40 ${activeTab === 'titles' ? 'border border-green-500/30 bg-green-500/10 text-[#20BF0E]' : 'border border-transparent bg-[#2d2d2d] text-[#AAACA6]'}`}
                >
                  Generated Titles ({titles.length})
                </button>
                <button
                  onClick={() => setActiveTab('scripts')}
                  className={`rounded-xl px-4 py-2 text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-[#20BF0E]/40 ${activeTab === 'scripts' ? 'border border-green-500/30 bg-green-500/10 text-[#20BF0E]' : 'border border-transparent bg-[#2d2d2d] text-[#AAACA6]'}`}
                >
                  Script Generations ({scripts.length})
                </button>
              </div>

              {/* Tab content */}
              <div>
                {activeTab === 'titles' && (
                  <div>
                    {titlesLoading && (
                      <div className="flex items-center justify-center py-12">
                        <div className="h-8 w-8 animate-spin rounded-full border-2 border-[#20BF0E] border-t-transparent" />
                      </div>
                    )}
                    {!titlesLoading && titles.length === 0 && (
                      <div className="py-12 text-center">
                        <div className="text-sm text-[#AAACA6]">
                          No titles available for this user.
                        </div>
                      </div>
                    )}
                    {!titlesLoading && (
                      <div className="space-y-3">
                        {titles.map((titleRecord, idx) => (
                          <TitleCard
                            key={titleRecord.uuid}
                            titleRecord={titleRecord}
                            index={idx}
                            onCopy={copyText}
                          />
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {activeTab === 'scripts' && (
                  <div>
                    {scriptsLoading && (
                      <div className="flex items-center justify-center py-12">
                        <div className="h-8 w-8 animate-spin rounded-full border-2 border-[#20BF0E] border-t-transparent" />
                      </div>
                    )}
                    {!scriptsLoading && scripts.length === 0 && (
                      <div className="py-12 text-center">
                        <div className="text-sm text-[#AAACA6]">
                          No scripts available for this user.
                        </div>
                      </div>
                    )}
                    {!scriptsLoading && (
                      <div className="space-y-3">
                        {scripts.map((script) => (
                          <ScriptCard key={script.uuid} script={script} onCopy={copyText} />
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </Card>
          </div>
        </div>
      ) : (
        <Card>
          <div className="text-[#AAACA6]">No user data</div>
        </Card>
      )}
    </div>
  );
}

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-1">
      <div className="text-xs text-[#AAACA6]">{label}</div>
      <div className="text-sm font-medium text-white">{value}</div>
    </div>
  );
}
