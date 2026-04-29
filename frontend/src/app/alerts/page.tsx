'use client'

import { useState, useEffect } from 'react'
import { AlertTriangle, Bell, Clock, Globe, Shield } from 'lucide-react'
import { Sidebar } from '@/components/layout/Sidebar'
import { cn, formatTimestamp, relativeTime, formatNumber } from '@/lib/utils'
import { getAlerts } from '@/lib/api'
import type { Alert, RiskLevel } from '@/types'

function RiskBadge({ level }: { level: RiskLevel }) {
  const cls = { CRITICAL:'badge-critical', HIGH:'badge-high', MEDIUM:'badge-medium', LOW:'badge-low', INFO:'badge-info' }[level] ?? 'badge-info'
  return <span className={cn('text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider', cls)}>{level}</span>
}

function RuleTag({ name }: { name: string }) {
  return <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-muted text-muted-foreground border border-border">{name}</span>
}

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'ALL' | RiskLevel>('ALL')

  useEffect(() => {
    getAlerts(40)
      .then(d => setAlerts(d.items))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const filtered = filter === 'ALL' ? alerts : alerts.filter(a => a.risk_level === filter)
  const criticalCount = alerts.filter(a => a.risk_level === 'CRITICAL').length
  const highCount = alerts.filter(a => a.risk_level === 'HIGH').length

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 z-10 bg-background/80 backdrop-blur border-b border-border px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold tracking-tight">Alerts</h1>
            <p className="text-xs text-muted-foreground mt-0.5">Active threat alerts requiring attention</p>
          </div>
          <div className="flex items-center gap-2">
            <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-xs font-medium">
              <AlertTriangle className="w-3 h-3" />
              {criticalCount} Critical
            </span>
            <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-orange-500/10 border border-orange-500/30 text-orange-400 text-xs font-medium">
              <Bell className="w-3 h-3" />
              {highCount} High
            </span>
          </div>
        </div>

        <div className="p-6 space-y-4 animate-fade-in">
          {/* Filter tabs */}
          <div className="flex items-center gap-2">
            {(['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'] as const).map(f => (
              <button key={f} onClick={() => setFilter(f)}
                className={cn('px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors',
                  filter === f ? 'bg-sky-500/15 border-sky-500/30 text-sky-300' : 'border-border text-muted-foreground hover:text-foreground hover:bg-muted'
                )}>
                {f}
              </button>
            ))}
            <span className="ml-auto text-xs text-muted-foreground">{formatNumber(filtered.length)} alerts</span>
          </div>

          {/* Alert list */}
          <div className="space-y-2">
            {loading ? (
              Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="card p-4 animate-pulse">
                  <div className="h-4 bg-muted rounded w-3/4" />
                  <div className="h-3 bg-muted rounded w-1/2 mt-2" />
                </div>
              ))
            ) : filtered.length === 0 ? (
              <div className="card p-12 text-center text-muted-foreground text-sm">No alerts found.</div>
            ) : (
              filtered.map(alert => (
                <div key={alert.alert_id}
                  className={cn('card p-4 flex items-start gap-4 hover:border-opacity-60 transition-all',
                    alert.risk_level === 'CRITICAL' && 'border-red-500/30 glow-critical'
                  )}>
                  {/* Icon */}
                  <div className={cn('w-9 h-9 rounded-lg flex items-center justify-center shrink-0',
                    alert.risk_level === 'CRITICAL' ? 'bg-red-500/15' : 'bg-orange-500/15'
                  )}>
                    <Shield className={cn('w-4 h-4', alert.risk_level === 'CRITICAL' ? 'text-red-400' : 'text-orange-400')} />
                  </div>

                  {/* Main content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <RiskBadge level={alert.risk_level} />
                      <RuleTag name={alert.rule_name} />
                      <span className="font-mono text-sm text-foreground truncate">{alert.ioc_value}</span>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1.5">{alert.description}</p>
                    <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1"><Globe className="w-3 h-3" />{alert.country_code ?? '—'}</span>
                      <span className="uppercase font-mono bg-muted px-1.5 py-0.5 rounded">{alert.ioc_type}</span>
                      <span>Score: <span className="text-foreground font-medium">{alert.risk_score.toFixed(0)}/100</span></span>
                      <span className="flex items-center gap-1 ml-auto"><Clock className="w-3 h-3" />{relativeTime(alert.created_at)}</span>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
