'use client'

import { useState, useEffect } from 'react'
import { Search, Filter, ChevronLeft, ChevronRight, ExternalLink } from 'lucide-react'
import { Sidebar } from '@/components/layout/Sidebar'
import { cn, riskBadgeClass, formatTimestamp, truncate, formatNumber } from '@/lib/utils'
import { getIoCs } from '@/lib/api'
import type { IoC, RiskLevel, IoCType } from '@/types'

const RISK_LEVELS: RiskLevel[] = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']
const IOC_TYPES:  IoCType[]    = ['ip', 'domain', 'hash', 'url']

// ── Risk Badge ────────────────────────────────────────────────────────────
function RiskBadge({ level }: { level: RiskLevel }) {
  return (
    <span className={cn('text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider', riskBadgeClass(level))}>
      {level}
    </span>
  )
}

// ── Risk Score Bar ────────────────────────────────────────────────────────
function RiskBar({ score, level }: { score: number; level: RiskLevel }) {
  const color = {
    CRITICAL: '#ef4444', HIGH: '#f97316', MEDIUM: '#eab308', LOW: '#22c55e', INFO: '#3b82f6',
  }[level]
  return (
    <div className="flex items-center gap-2">
      <div className="w-20 h-1.5 rounded-full bg-muted overflow-hidden">
        <div className="h-full rounded-full transition-all" style={{ width: `${score}%`, background: color }} />
      </div>
      <span className="text-xs font-mono text-muted-foreground">{score.toFixed(0)}</span>
    </div>
  )
}

// ── Main page ─────────────────────────────────────────────────────────────
export default function IoCsPage() {
  const [iocs, setIoCs]       = useState<IoC[]>([])
  const [total, setTotal]     = useState(0)
  const [page, setPage]       = useState(1)
  const [pages, setPages]     = useState(1)
  const [loading, setLoading] = useState(true)
  const [search, setSearch]   = useState('')
  const [filterRisk, setFilterRisk]  = useState<RiskLevel | ''>('')
  const [filterType, setFilterType]  = useState<IoCType | ''>('')
  const PAGE_SIZE = 20

  useEffect(() => {
    setLoading(true)
    getIoCs({
      page,
      size:       PAGE_SIZE,
      risk_level: filterRisk  || undefined,
      ioc_type:   filterType  || undefined,
    })
      .then(data => {
        setIoCs(data.items)
        setTotal(data.total)
        setPages(data.pages)
      })
      .catch(() => {/* use empty state */})
      .finally(() => setLoading(false))
  }, [page, filterRisk, filterType])

  const filtered = search
    ? iocs.filter(i => i.ioc_value.includes(search) || i.tags.some(t => t.includes(search)))
    : iocs

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />

      <main className="flex-1 overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 z-10 bg-background/80 backdrop-blur border-b border-border px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold tracking-tight">IoC Explorer</h1>
              <p className="text-xs text-muted-foreground mt-0.5">
                {formatNumber(total)} indicators in database
              </p>
            </div>
          </div>
        </div>

        <div className="p-6 space-y-4 animate-fade-in">
          {/* Filters */}
          <div className="card p-4 flex flex-wrap items-center gap-3">
            {/* Search */}
            <div className="relative flex-1 min-w-60">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search by value, tag…"
                value={search}
                onChange={e => setSearch(e.target.value)}
                className="w-full pl-9 pr-3 py-2 bg-muted rounded-lg text-sm border border-border focus:outline-none focus:border-sky-500/50 placeholder:text-muted-foreground"
              />
            </div>

            {/* Risk level filter */}
            <select
              value={filterRisk}
              onChange={e => { setFilterRisk(e.target.value as RiskLevel | ''); setPage(1) }}
              className="px-3 py-2 bg-muted rounded-lg text-sm border border-border focus:outline-none focus:border-sky-500/50 text-foreground"
            >
              <option value="">All risk levels</option>
              {RISK_LEVELS.map(l => <option key={l} value={l}>{l}</option>)}
            </select>

            {/* IoC type filter */}
            <select
              value={filterType}
              onChange={e => { setFilterType(e.target.value as IoCType | ''); setPage(1) }}
              className="px-3 py-2 bg-muted rounded-lg text-sm border border-border focus:outline-none focus:border-sky-500/50 text-foreground"
            >
              <option value="">All types</option>
              {IOC_TYPES.map(t => <option key={t} value={t}>{t.toUpperCase()}</option>)}
            </select>
          </div>

          {/* Table */}
          <div className="card overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border">
                    {['Risk', 'Type', 'Value', 'Source', 'Country', 'ASN', 'Score', 'Tags', 'Seen'].map(h => (
                      <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider whitespace-nowrap">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {loading ? (
                    Array.from({ length: 8 }).map((_, i) => (
                      <tr key={i} className="border-b border-border/50">
                        {Array.from({ length: 9 }).map((_, j) => (
                          <td key={j} className="px-4 py-3">
                            <div className="h-3 bg-muted rounded animate-pulse" />
                          </td>
                        ))}
                      </tr>
                    ))
                  ) : filtered.length === 0 ? (
                    <tr>
                      <td colSpan={9} className="px-4 py-12 text-center text-muted-foreground text-xs">
                        No IoCs found matching your filters.
                      </td>
                    </tr>
                  ) : (
                    filtered.map(ioc => (
                      <tr
                        key={ioc.event_id}
                        className="border-b border-border/50 hover:bg-muted/40 transition-colors group"
                      >
                        <td className="px-4 py-3"><RiskBadge level={ioc.risk_level} /></td>
                        <td className="px-4 py-3">
                          <span className="font-mono text-xs bg-muted px-1.5 py-0.5 rounded uppercase">{ioc.ioc_type}</span>
                        </td>
                        <td className="px-4 py-3 font-mono text-xs max-w-[200px]">
                          <span title={ioc.ioc_value}>{truncate(ioc.ioc_value, 32)}</span>
                        </td>
                        <td className="px-4 py-3 text-muted-foreground text-xs">{ioc.source}</td>
                        <td className="px-4 py-3 text-xs">{ioc.country_code ?? '—'}</td>
                        <td className="px-4 py-3 text-xs text-muted-foreground font-mono">{ioc.asn ?? '—'}</td>
                        <td className="px-4 py-3"><RiskBar score={ioc.risk_score} level={ioc.risk_level} /></td>
                        <td className="px-4 py-3">
                          <div className="flex flex-wrap gap-1 max-w-[160px]">
                            {ioc.tags.slice(0, 2).map(tag => (
                              <span key={tag} className="text-[10px] px-1.5 py-0.5 rounded bg-muted text-muted-foreground">
                                {tag}
                              </span>
                            ))}
                            {ioc.tags.length > 2 && (
                              <span className="text-[10px] text-muted-foreground">+{ioc.tags.length - 2}</span>
                            )}
                          </div>
                        </td>
                        <td className="px-4 py-3 text-xs text-muted-foreground whitespace-nowrap">
                          {formatTimestamp(ioc.ingested_at)}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="flex items-center justify-between px-4 py-3 border-t border-border">
              <p className="text-xs text-muted-foreground">
                Page {page} of {pages} · {formatNumber(total)} total
              </p>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="p-1.5 rounded-lg border border-border disabled:opacity-30 hover:bg-muted transition-colors"
                >
                  <ChevronLeft className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => setPage(p => Math.min(pages, p + 1))}
                  disabled={page === pages}
                  className="p-1.5 rounded-lg border border-border disabled:opacity-30 hover:bg-muted transition-colors"
                >
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
