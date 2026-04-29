// ── IoC Types ──────────────────────────────────────────────────────────

export type IoCType    = 'ip' | 'domain' | 'hash' | 'url'
export type RiskLevel  = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO'
export type IoCSource  = 'abuseipdb' | 'virustotal' | 'alienvault_otx' | 'feodo_tracker' | 'urlhaus' | 'mock'

export interface IoC {
  event_id:     string
  ioc_type:     IoCType
  ioc_value:    string
  source:       IoCSource | string
  confidence:   number
  tags:         string[]
  country_code: string | null
  country_name: string | null
  asn:          string | null
  isp:          string | null
  abuse_score:  number | null
  risk_score:   number
  risk_level:   RiskLevel
  ingested_at:  number
  enriched_at:  number | null
}

export interface PaginatedIoCs {
  items: IoC[]
  total: number
  page:  number
  size:  number
  pages: number
}

// ── Alert Types ────────────────────────────────────────────────────────

export interface Alert {
  alert_id:    string
  event_id:    string
  ioc_value:   string
  ioc_type:    IoCType
  risk_level:  RiskLevel
  risk_score:  number
  rule_name:   string
  description: string
  country_code:string | null
  created_at:  number
}

// ── Stats Types ────────────────────────────────────────────────────────

export interface DashboardSummary {
  total_iocs:        number
  iocs_last_24h:     number
  critical_alerts:   number
  high_alerts:       number
  sources_active:    number
  avg_risk_score:    number
  top_ioc_type:      IoCType
  top_country:       string
  processing_lag_ms: number
}

export interface IoCTypeStats {
  type:  IoCType
  count: number
  pct:   number
}

export interface CountryStats {
  country_code: string
  country_name: string
  count:        number
}

export interface TimelinePoint {
  hour:     number
  count:    number
  critical: number
}

// ── API Response wrapper ───────────────────────────────────────────────

export interface ApiResponse<T> {
  data:    T
  error?:  string
  status:  number
}
