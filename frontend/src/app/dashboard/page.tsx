'use client'

import { useEffect, useState, useCallback } from 'react'
import {
  Shield, AlertTriangle, Activity, Globe, Zap,
  TrendingUp, Clock, Server, RefreshCw,
} from 'lucide-react'
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts'
import { Sidebar } from '@/components/layout/Sidebar'
import { cn, formatNumber, riskColor, relativeTime } from '@/lib/utils'
import { createIoCStream } from '@/lib/api'
import type { DashboardSummary, TimelinePoint, IoCTypeStats, CountryStats, RiskLevel } from '@/types'

// ── Mock data for initial render ──────────────────────────────────────────
const mockSummary: DashboardSummary = {
  total_iocs:        10_284,
  iocs_last_24h:     432,
  critical_alerts:   18,
  high_alerts:       76,
  sources_active:    4,
  avg_risk_score:    52.4,
  top_ioc_type:      'ip',
  top_country:       'RU',
  processing_lag_ms: 312,
}

const mockTimeline: TimelinePoint[] = Array.from({ length: 24 }, (_, i) => ({
  hour:     Date.now() - (23 - i) * 3_600_000,
  count:    Math.floor(Math.random() * 80) + 10,
  critical: Math.floor(Math.random() * 8),
}))

const mockTypes: IoCTypeStats[] = [
  { type: 'ip',     count: 4_923, pct: 48 },
  { type: 'domain', count: 2_671, pct: 26 },
  { type: 'hash',   count: 1_641, pct: 16 },
  { type: 'url',    count: 1_049, pct: 10 },
]

const mockCountries: CountryStats[] = [
  { country_code: 'RU', country_name: 'Russia',        count: 2_847 },
  { country_code: 'CN', country_name: 'China',         count: 2_103 },
  { country_code: 'US', country_name: 'United States', count: 1_029 },
  { country_code: 'DE', country_name: 'Germany',       count:   621 },
  { country_code: 'NL', country_name: 'Netherlands',   count:   498 },
  { country_code: 'UA', country_name: 'Ukraine',       count:   381 },
]

const PIE_COLORS = ['#0ea5e9', '#818cf8', '#34d399', '#fb923c']

// ── Live feed item ────────────────────────────────────────────────────────
interface LiveItem {
  id:          string
  ioc_value:   string
  ioc_type:    string
  risk_level:  RiskLevel
  risk_score:  number
  country_code:string
  ingested_at: number
}

// ── Stat Card ─────────────────────────────────────────────────────────────
function StatCard({
  icon: Icon, label, value, sub, accent = false, danger = false,
}: {
  icon: React.ElementType
  label: string
  value: string | number
  sub?: string
  accent?: boolean
  danger?: boolean
}) {
  return (
    <div className={cn(
      'card p-5 flex flex-col gap-3 transition-all duration-200 hover:border-opacity-60',
      danger  && 'border-red-500/40 glow-critical',
      accent  && 'border-sky-500/30',
    )}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium tracking-widest uppercase text-muted-foreground">{label}</span>
        <div className={cn(
          'w-8 h-8 rounded-lg flex items-center justify-center',
          danger ? 'bg-red-500/15' : accent ? 'bg-sky-500/15' : 'bg-muted',
        )}>
          <Icon className={cn(
            'w-4 h-4',
            danger ? 'text-red-400' : accent ? 'text-sky-400' : 'text-muted-foreground',
          )} />
        </div>
      </div>
      <div>
        <p className="text-2xl font-bold tracking-tight">{typeof value === 'number' ? formatNumber(value) : value}</p>
        {sub && <p className="text-xs text-muted-foreground mt-1">{sub}</p>}
      </div>
    </div>
  )
}

// ── Risk badge ────────────────────────────────────────────────────────────
function RiskBadge({ level }: { level: RiskLevel }) {
  const cls = {
    CRITICAL: 'badge-critical',
    HIGH:     'badge-high',
    MEDIUM:   'badge-medium',
    LOW:      'badge-low',
    INFO:     'badge-info',
  }[level] ?? 'badge-info'
  return (
    <span className={cn('text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider', cls)}>
      {level}
    </span>
  )
}

// ── Main Dashboard ────────────────────────────────────────────────────────
export default function DashboardPage() {
  const [summary]  = useState<DashboardSummary>(mockSummary)
  const [timeline] = useState<TimelinePoint[]>(mockTimeline)
  const [liveItems, setLiveItems] = useState<LiveItem[]>([])
  const [isLive, setIsLive] = useState(true)
  const [totalReceived, setTotalReceived] = useState(0)

  const addLiveItem = useCallback((raw: Partial<LiveItem>) => {
    if (!raw.ioc_value) return
    const item: LiveItem = {
      id:           raw.id ?? Math.random().toString(36).slice(2),
      ioc_value:    raw.ioc_value,
      ioc_type:     raw.ioc_type ?? 'ip',
      risk_level:   (raw.risk_level as RiskLevel) ?? 'INFO',
      risk_score:   raw.risk_score ?? 0,
      country_code: raw.country_code ?? '??',
      ingested_at:  raw.ingested_at ?? Date.now(),
    }
    setLiveItems(prev => [item, ...prev].slice(0, 50))
    setTotalReceived(n => n + 1)
  }, [])

  useEffect(() => {
    if (!isLive) return
    const es = createIoCStream(addLiveItem)
    return () => es.close()
  }, [isLive, addLiveItem])

  const timelineFormatted = timeline.map(p => ({
    ...p,
    label: new Date(p.hour).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' }),
  }))

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />

      <main className="flex-1 overflow-y-auto">
        {/* ── Header ── */}
        <div className="sticky top-0 z-10 bg-background/80 backdrop-blur border-b border-border px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold tracking-tight">Dashboard</h1>
            <p className="text-xs text-muted-foreground mt-0.5">Real-time threat intelligence overview</p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsLive(v => !v)}
              className={cn(
                'flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors',
                isLive
                  ? 'border-green-500/40 bg-green-500/10 text-green-400'
                  : 'border-border text-muted-foreground hover:border-border',
              )}
            >
              {isLive ? <span className="live-dot" /> : <RefreshCw className="w-3 h-3" />}
              {isLive ? 'LIVE' : 'PAUSED'}
            </button>
            <div className="text-xs text-muted-foreground">
              {formatNumber(totalReceived)} events received
            </div>
          </div>
        </div>

        <div className="p-6 space-y-6 animate-fade-in">

          {/* ── Stat cards ── */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard icon={Shield}       label="Total IoCs"        value={summary.total_iocs}      sub="All time"                  accent />
            <StatCard icon={Activity}     label="Last 24h"          value={summary.iocs_last_24h}   sub="New indicators"            />
            <StatCard icon={AlertTriangle} label="Critical Alerts"  value={summary.critical_alerts} sub="Requires immediate action" danger />
            <StatCard icon={Zap}          label="Avg Risk Score"    value={`${summary.avg_risk_score}/100`} sub="Across all IoCs"  />
          </div>

          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard icon={TrendingUp} label="High Alerts"    value={summary.high_alerts}       sub="Active"              />
            <StatCard icon={Server}     label="Active Sources" value={summary.sources_active}    sub="Feed connectors"     />
            <StatCard icon={Globe}      label="Top Country"    value={summary.top_country}        sub="By IoC volume"       />
            <StatCard icon={Clock}      label="Processing Lag" value={`${summary.processing_lag_ms}ms`} sub="Spark pipeline" />
          </div>

          {/* ── Charts row ── */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">

            {/* Timeline chart */}
            <div className="card p-5 lg:col-span-2">
              <h2 className="text-sm font-semibold mb-4 text-foreground">IoC Ingestion — Last 24h</h2>
              <ResponsiveContainer width="100%" height={200}>
                <AreaChart data={timelineFormatted} margin={{ top: 0, right: 0, bottom: 0, left: -20 }}>
                  <defs>
                    <linearGradient id="gradCount" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor="#0ea5e9" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0}   />
                    </linearGradient>
                    <linearGradient id="gradCrit" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor="#ef4444" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#ef4444" stopOpacity={0}   />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(220,13%,18%)" />
                  <XAxis dataKey="label" tick={{ fontSize: 10, fill: 'hsl(215,16%,55%)' }} tickLine={false} interval={3} />
                  <YAxis tick={{ fontSize: 10, fill: 'hsl(215,16%,55%)' }} tickLine={false} axisLine={false} />
                  <Tooltip
                    contentStyle={{ background: 'hsl(220,14%,10%)', border: '1px solid hsl(220,13%,18%)', borderRadius: 6, fontSize: 12 }}
                    labelStyle={{ color: 'hsl(210,20%,92%)' }}
                  />
                  <Area type="monotone" dataKey="count"    stroke="#0ea5e9" fill="url(#gradCount)" strokeWidth={2} name="Total" />
                  <Area type="monotone" dataKey="critical" stroke="#ef4444" fill="url(#gradCrit)"  strokeWidth={1.5} name="Critical" />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            {/* IoC type distribution */}
            <div className="card p-5">
              <h2 className="text-sm font-semibold mb-4 text-foreground">IoC Types</h2>
              <ResponsiveContainer width="100%" height={140}>
                <PieChart>
                  <Pie data={mockTypes} dataKey="count" nameKey="type" cx="50%" cy="50%" innerRadius={40} outerRadius={65} paddingAngle={3}>
                    {mockTypes.map((_, i) => (
                      <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ background: 'hsl(220,14%,10%)', border: '1px solid hsl(220,13%,18%)', fontSize: 12 }}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="space-y-1.5 mt-2">
                {mockTypes.map((t, i) => (
                  <div key={t.type} className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full" style={{ background: PIE_COLORS[i] }} />
                      <span className="uppercase text-muted-foreground font-mono">{t.type}</span>
                    </div>
                    <span className="font-medium">{t.pct}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* ── Bottom row: countries + live feed ── */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">

            {/* Country bar chart */}
            <div className="card p-5">
              <h2 className="text-sm font-semibold mb-4 text-foreground">Top Countries by Volume</h2>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={mockCountries} layout="vertical" margin={{ left: 0, right: 0 }}>
                  <XAxis type="number" tick={{ fontSize: 10, fill: 'hsl(215,16%,55%)' }} tickLine={false} axisLine={false} />
                  <YAxis type="category" dataKey="country_code" tick={{ fontSize: 11, fill: 'hsl(210,20%,92%)' }} tickLine={false} axisLine={false} width={30} />
                  <Tooltip
                    contentStyle={{ background: 'hsl(220,14%,10%)', border: '1px solid hsl(220,13%,18%)', fontSize: 12 }}
                    formatter={(v: number) => [formatNumber(v), 'IoCs']}
                  />
                  <Bar dataKey="count" fill="#818cf8" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Live event feed */}
            <div className="card p-5 flex flex-col">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-sm font-semibold text-foreground">Live Event Feed</h2>
                <div className="flex items-center gap-2 text-xs text-green-400">
                  <span className="live-dot" />
                  Streaming
                </div>
              </div>

              <div className="flex-1 overflow-y-auto space-y-2 min-h-[200px] max-h-[220px] pr-1">
                {liveItems.length === 0 ? (
                  <div className="flex items-center justify-center h-full text-muted-foreground text-xs">
                    Waiting for events…
                  </div>
                ) : (
                  liveItems.map(item => (
                    <div
                      key={item.id}
                      className="flex items-center gap-3 p-2.5 rounded-lg bg-muted/50 text-xs animate-slide-up"
                    >
                      <RiskBadge level={item.risk_level} />
                      <span className="font-mono text-foreground truncate flex-1" title={item.ioc_value}>
                        {item.ioc_value.length > 28 ? item.ioc_value.slice(0, 28) + '…' : item.ioc_value}
                      </span>
                      <span className="text-muted-foreground uppercase">{item.ioc_type}</span>
                      <span className="text-muted-foreground font-mono">{item.country_code}</span>
                      <span className="text-muted-foreground whitespace-nowrap">{relativeTime(item.ingested_at)}</span>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
