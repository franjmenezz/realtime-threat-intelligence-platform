'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard, ShieldAlert, Search,
  Bell, Settings, LogOut, Activity,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const NAV_ITEMS = [
  { href: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { href: '/iocs',      icon: Search,          label: 'IoC Explorer' },
  { href: '/alerts',    icon: Bell,            label: 'Alerts' },
  { href: '/settings',  icon: Settings,        label: 'Settings' },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-56 h-screen flex flex-col border-r border-border bg-card shrink-0">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-border">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-sky-500/20 border border-sky-500/30 flex items-center justify-center">
            <ShieldAlert className="w-4 h-4 text-sky-400" />
          </div>
          <div>
            <p className="text-sm font-bold tracking-tight leading-none">TI Pipeline</p>
            <p className="text-[10px] text-muted-foreground mt-0.5">Threat Intelligence</p>
          </div>
        </div>
      </div>

      {/* Status indicator */}
      <div className="mx-3 mt-3 px-3 py-2 rounded-lg bg-green-500/10 border border-green-500/20 flex items-center gap-2">
        <Activity className="w-3 h-3 text-green-400" />
        <span className="text-[10px] font-medium text-green-400 uppercase tracking-wider">Pipeline Active</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-2 py-3 space-y-0.5">
        {NAV_ITEMS.map(({ href, icon: Icon, label }) => {
          const active = pathname === href || pathname.startsWith(href + '/')
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors',
                active
                  ? 'bg-sky-500/15 text-sky-300 border border-sky-500/20'
                  : 'text-muted-foreground hover:text-foreground hover:bg-muted',
              )}
            >
              <Icon className="w-4 h-4 shrink-0" />
              {label}
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="p-3 border-t border-border space-y-1">
        <div className="px-3 py-2 rounded-lg bg-muted flex items-center gap-2">
          <div className="w-6 h-6 rounded-full bg-sky-500/30 flex items-center justify-center text-[10px] font-bold text-sky-300">
            A
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-medium truncate">Admin</p>
            <p className="text-[10px] text-muted-foreground truncate">admin@threatintel.local</p>
          </div>
        </div>
        <button className="flex items-center gap-3 w-full px-3 py-2 rounded-lg text-xs text-muted-foreground hover:text-foreground hover:bg-muted transition-colors">
          <LogOut className="w-3.5 h-3.5" />
          Sign out
        </button>
      </div>
    </aside>
  )
}
