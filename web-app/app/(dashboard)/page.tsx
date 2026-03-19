import Link from 'next/link';
import {
  BookOpen,
  Box,
  Clock,
  FileText,
  FileVideo,
  LayoutTemplate,
  ListOrdered,
  Mic,
  Minus,
  Sparkles,
  TrendingUp,
  Zap,
} from 'lucide-react';

import { getScriptGenerations } from './my-scripts/actions';
import { Badge } from 'components/ui/Badge';
import { Button } from 'components/ui/Button';

// ── Helpers ──────────────────────────────────────────────────────────
function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

function getWordCountLabel(count?: number) {
  if (!count) return null;
  if (count >= 1000) return `${(count / 1000).toFixed(1)}k words`;
  return `${count} words`;
}

// ── Stat card ─────────────────────────────────────────────────────────
function StatCard({
  title,
  value,
  trend,
  trendNeutral,
  icon: Icon,
}: {
  title: string;
  value: string | number;
  trend?: string;
  trendNeutral?: boolean;
  icon: React.ElementType;
}) {
  return (
    <div className="flex flex-col gap-3 rounded-lg border border-border bg-card p-5">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-muted-foreground">{title}</p>
        <div className="flex h-8 w-8 items-center justify-center rounded-md bg-secondary">
          <Icon className="h-[18px] w-[18px] text-secondary-foreground" />
        </div>
      </div>
      <p className="text-[28px] font-semibold leading-none tracking-tight text-foreground">
        {value}
      </p>
      {trend && (
        <div
          className={`flex items-center gap-1 text-[13px] font-medium ${trendNeutral ? 'text-muted-foreground' : 'text-success'}`}
        >
          {trendNeutral ? (
            <Minus className="h-3.5 w-3.5" />
          ) : (
            <TrendingUp className="h-3.5 w-3.5" />
          )}
          {trend}
        </div>
      )}
    </div>
  );
}

// ── Quick action card ─────────────────────────────────────────────────
function ActionCard({
  title,
  desc,
  icon: Icon,
  href,
  primary,
}: {
  title: string;
  desc: string;
  icon: React.ElementType;
  href: string;
  primary?: boolean;
}) {
  return (
    <Link
      href={href}
      className="flex items-center gap-4 rounded-lg border border-border bg-card p-5 transition-colors hover:border-primary/30 hover:bg-accent/10"
    >
      <div
        className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-md ${
          primary ? 'bg-primary text-primary-foreground' : 'bg-secondary text-secondary-foreground'
        }`}
      >
        <Icon className="h-6 w-6" />
      </div>
      <div className="flex flex-col gap-1">
        <p className="text-base font-semibold text-foreground">{title}</p>
        <p className="text-[13px] font-medium text-muted-foreground">{desc}</p>
      </div>
    </Link>
  );
}

// ── Page ─────────────────────────────────────────────────────────────
export default async function DashboardPage() {
  const [{ data: scriptsData }, { data: outlinesData }, { data: recentData }] = await Promise.all([
    getScriptGenerations({ type: 'script', limit: 1 }),
    getScriptGenerations({ type: 'outline', limit: 1 }),
    getScriptGenerations({ limit: 4, ordering: 'modified' }),
  ]);

  const totalScripts = scriptsData?.count ?? 0;
  const totalOutlines = outlinesData?.count ?? 0;
  const recentItems = recentData?.results ?? [];

  return (
    <div className="space-y-6 px-4 py-6 sm:px-7">
      {/* ── Stats grid ── */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard
          title="Scripts Generated"
          value={totalScripts}
          trend={totalScripts > 0 ? `+${totalScripts} total` : undefined}
          icon={FileText}
        />
        <StatCard
          title="Outlines Created"
          value={totalOutlines}
          trend="No change"
          trendNeutral
          icon={ListOrdered}
        />
        <StatCard
          title="Total Creations"
          value={totalScripts + totalOutlines}
          trend={
            totalScripts + totalOutlines > 0 ? `+${totalScripts + totalOutlines} total` : undefined
          }
          icon={Sparkles}
        />
        <StatCard
          title="Recent Activity"
          value={recentItems.length}
          trend="Resets monthly"
          trendNeutral
          icon={Zap}
        />
      </div>

      {/* ── Quick actions ── */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <ActionCard
          title="New Script"
          desc="Start from scratch or prompt"
          icon={Sparkles}
          href="/new-script"
          primary
        />
        <ActionCard
          title="Generate Titles"
          desc="Create catchy YouTube titles"
          icon={LayoutTemplate}
          href="/title-generation"
        />
        <ActionCard
          title="Browse Niches"
          desc="Explore niche ideas & styles"
          icon={Mic}
          href="/niche-vault"
        />
      </div>

      {/* ── Main grid ── */}
      <div className="grid gap-6 lg:grid-cols-[minmax(0,1.5fr)_minmax(300px,1fr)]">
        {/* Recent scripts */}
        <div className="flex flex-col rounded-lg border border-border bg-card">
          <div className="flex items-center justify-between border-b border-border px-4 py-5 sm:px-6">
            <h2 className="text-[18px] font-semibold text-foreground">Recent Projects</h2>
            <Link href="/my-scripts" className="text-sm font-medium text-primary hover:underline">
              View all
            </Link>
          </div>
          {recentItems.length > 0 ? (
            <ul className="flex flex-col divide-y divide-border">
              {recentItems.map((item) => (
                <li key={item.uuid}>
                  <Link
                    href={
                      item.type === 'script'
                        ? `/new-script/script/${item.uuid}`
                        : `/new-script/${item.uuid}`
                    }
                    className="flex items-center justify-between gap-4 px-4 py-4 transition-colors hover:bg-muted/50 sm:px-6"
                  >
                    <div className="flex min-w-0 items-center gap-4">
                      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-secondary text-secondary-foreground">
                        <FileVideo className="h-5 w-5" />
                      </div>
                      <div className="flex min-w-0 flex-col gap-1">
                        <p className="truncate text-[15px] font-semibold text-foreground">
                          {item.title || 'Untitled'}
                        </p>
                        <div className="flex items-center gap-2 text-[13px] font-medium text-muted-foreground">
                          <Clock className="h-3 w-3" />
                          <span>{formatDate(item.modified || item.created)}</span>
                          {getWordCountLabel(item.word_count ?? undefined) && (
                            <>
                              <span>·</span>
                              <span>{getWordCountLabel(item.word_count ?? undefined)}</span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                    <Badge
                      variant={item.type === 'script' ? 'primary' : 'default'}
                      size="sm"
                      className="shrink-0"
                    >
                      {item.type === 'script' ? 'Script' : 'Outline'}
                    </Badge>
                  </Link>
                </li>
              ))}
            </ul>
          ) : (
            <div className="flex flex-col items-center justify-center px-4 py-16 text-center sm:px-6">
              <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-muted">
                <FileText className="h-5 w-5 text-muted-foreground" />
              </div>
              <p className="text-sm font-medium text-foreground">No scripts yet</p>
              <p className="mt-1 text-xs text-muted-foreground">
                Generate your first script to get started.
              </p>
              <Button asChild size="sm" className="mt-4">
                <Link href="/new-script">
                  <Sparkles className="h-3.5 w-3.5" />
                  Create your first script
                </Link>
              </Button>
            </div>
          )}
        </div>

        {/* Top Templates */}
        <div className="flex flex-col rounded-lg border border-border bg-card">
          <div className="flex items-center justify-between border-b border-border px-4 py-5 sm:px-6">
            <h2 className="text-[18px] font-semibold text-foreground">Top Templates</h2>
            <Link href="/niche-vault" className="text-sm font-medium text-primary hover:underline">
              Explore
            </Link>
          </div>
          <div className="flex flex-col gap-4 p-4 sm:p-6">
            {[
              {
                icon: ListOrdered,
                name: 'Top 10 Listicles',
                desc: 'High retention format perfect for tech, finance, and productivity niches.',
              },
              {
                icon: Box,
                name: 'Tech Product Review',
                desc: 'Structured for unbiased pros/cons, unboxing b-roll, and affiliate CTA.',
              },
              {
                icon: BookOpen,
                name: 'Storytime / Vlog',
                desc: 'Narrative arc focused on conflict, realization, and resolution.',
              },
            ].map((t) => {
              const TIcon = t.icon;
              return (
                <div key={t.name} className="flex items-start gap-4 rounded-md bg-secondary p-4">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-card text-foreground">
                    <TIcon className="h-5 w-5" />
                  </div>
                  <div className="flex flex-col gap-1.5">
                    <p className="text-sm font-semibold text-foreground">{t.name}</p>
                    <p className="text-[13px] font-medium leading-relaxed text-muted-foreground">
                      {t.desc}
                    </p>
                    <Link
                      href="/new-script"
                      className="mt-1 text-xs font-semibold text-primary hover:underline"
                    >
                      Use template →
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
