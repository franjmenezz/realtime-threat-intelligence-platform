'use client'

import { useState } from 'react'
import { Key, Database, Zap, Bell, Save, Eye, EyeOff } from 'lucide-react'
import { Sidebar } from '@/components/layout/Sidebar'
import { cn } from '@/lib/utils'
import toast from 'react-hot-toast'

function Section({ title, icon: Icon, children }: { title: string; icon: React.ElementType; children: React.ReactNode }) {
  return (
    <div className="card p-5 space-y-4">
      <div className="flex items-center gap-2 pb-3 border-b border-border">
        <div className="w-7 h-7 rounded-lg bg-sky-500/15 flex items-center justify-center">
          <Icon className="w-3.5 h-3.5 text-sky-400" />
        </div>
        <h2 className="text-sm font-semibold">{title}</h2>
      </div>
      {children}
    </div>
  )
}

function Field({ label, placeholder, value, onChange, type = 'text', hint }: { label: string; placeholder?: string; value: string; onChange: (v: string) => void; type?: string; hint?: string }) {
  const [show, setShow] = useState(false)
  const isPassword = type === 'password'
  return (
    <div className="space-y-1.5">
      <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">{label}</label>
      <div className="relative">
        <input
          type={isPassword && !show ? 'password' : 'text'}
          value={value}
          onChange={e => onChange(e.target.value)}
          placeholder={placeholder}
          className="w-full px-3 py-2 bg-muted rounded-lg text-sm border border-border focus:outline-none focus:border-sky-500/50 placeholder:text-muted-foreground pr-9"
        />
        {isPassword && (
          <button onClick={() => setShow(v => !v)} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground">
            {show ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
          </button>
        )}
      </div>
      {hint && <p className="text-[11px] text-muted-foreground">{hint}</p>}
    </div>
  )
}

function Toggle({ label, description, value, onChange }: { label: string; description: string; value: boolean; onChange: (v: boolean) => void }) {
  return (
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm font-medium">{label}</p>
        <p className="text-xs text-muted-foreground mt-0.5">{description}</p>
      </div>
      <button onClick={() => onChange(!value)}
        className={cn('relative w-10 h-5 rounded-full transition-colors', value ? 'bg-sky-500' : 'bg-muted border border-border')}>
        <span className={cn('absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform shadow-sm', value ? 'translate-x-5' : 'translate-x-0.5')} />
      </button>
    </div>
  )
}

export default function SettingsPage() {
  const [abuseKey, setAbuseKey] = useState('')
  const [vtKey, setVtKey] = useState('')
  const [otxKey, setOtxKey] = useState('')
  const [mockEnabled, setMockEnabled] = useState(true)
  const [mockInterval, setMockInterval] = useState('3')
  const [alertCritical, setAlertCritical] = useState(true)
  const [alertHigh, setAlertHigh] = useState(true)

  const handleSave = () => {
    toast.success('Settings saved successfully')
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <div className="sticky top-0 z-10 bg-background/80 backdrop-blur border-b border-border px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold tracking-tight">Settings</h1>
            <p className="text-xs text-muted-foreground mt-0.5">Configure pipeline sources and alerts</p>
          </div>
          <button onClick={handleSave}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-sky-500 hover:bg-sky-400 text-white text-sm font-medium transition-colors">
            <Save className="w-3.5 h-3.5" />
            Save changes
          </button>
        </div>

        <div className="p-6 space-y-4 max-w-2xl animate-fade-in">
          <Section title="OSINT API Keys" icon={Key}>
            <Field label="AbuseIPDB API Key" placeholder="Get free key at abuseipdb.com" value={abuseKey} onChange={setAbuseKey} type="password" hint="1,000 free queries/day — used for IP reputation scoring" />
            <Field label="VirusTotal API Key" placeholder="Get free key at virustotal.com" value={vtKey} onChange={setVtKey} type="password" hint="500 free queries/day — used for hash and URL analysis" />
            <Field label="AlienVault OTX API Key" placeholder="Get free key at otx.alienvault.com" value={otxKey} onChange={setOtxKey} type="password" hint="Unlimited free — community threat intelligence feeds" />
          </Section>

          <Section title="Mock Feed" icon={Zap}>
            <Toggle label="Enable mock feed" description="Generate simulated IoC events for development and testing" value={mockEnabled} onChange={setMockEnabled} />
            <Field label="Interval (seconds)" placeholder="3" value={mockInterval} onChange={setMockInterval} hint="How often to publish a batch of mock IoCs to Kafka" />
          </Section>

          <Section title="Alert Notifications" icon={Bell}>
            <Toggle label="Critical alerts" description="Trigger alerts for IoCs with risk score ≥ 80" value={alertCritical} onChange={setAlertCritical} />
            <Toggle label="High alerts" description="Trigger alerts for IoCs with risk score ≥ 60" value={alertHigh} onChange={setAlertHigh} />
          </Section>

          <Section title="Database" icon={Database}>
            <div className="flex items-center justify-between p-3 rounded-lg bg-muted">
              <div>
                <p className="text-xs font-medium">PostgreSQL</p>
                <p className="text-[11px] text-muted-foreground mt-0.5">postgres:5432 / threatintel</p>
              </div>
              <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-green-500/15 text-green-400 border border-green-500/30">Connected</span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-muted">
              <div>
                <p className="text-xs font-medium">Apache Kafka</p>
                <p className="text-[11px] text-muted-foreground mt-0.5">kafka:29092 — 3 topics active</p>
              </div>
              <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-green-500/15 text-green-400 border border-green-500/30">Connected</span>
            </div>
          </Section>
        </div>
      </main>
    </div>
  )
}
