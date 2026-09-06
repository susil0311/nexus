'use client'

import { useEffect, useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Zap, LayoutDashboard, Upload, CheckSquare, Calendar,
  Brain, MessageSquare, AlertTriangle, Map, Settings,
  ChevronLeft, ChevronRight, Bell, ChevronDown, LogOut,
  User, Menu, X,
} from 'lucide-react'
import { useStore, useAuth, useSidebar, useNotifications } from '@/lib/store'
import { projectsApi } from '@/lib/api'
import { mockProjects } from '@/lib/mock-data'
import { cn } from '@/lib/utils'

// ─── Nav Items ────────────────────────────────────────────────────────────────
const NAV_ITEMS = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/ingest', label: 'AI Ingestion', icon: Upload },
  { href: '/review', label: 'Review Queue', icon: CheckSquare, badge: 'queue' },
  { href: '/schedule', label: 'Schedule', icon: Calendar },
  { href: '/analytics', label: 'AI Intelligence', icon: Brain },
  { href: '/memory', label: 'Memory Copilot', icon: MessageSquare },
  { href: '/anomalies', label: 'Anomalies', icon: AlertTriangle, badge: 'anomaly' },
  { href: '/map', label: 'GIS Map', icon: Map },
  { href: '/admin', label: 'Admin', icon: Settings },
]

// ─── Sidebar Nav Item ─────────────────────────────────────────────────────────
function NavItem({
  item,
  collapsed,
  pathname,
}: {
  item: typeof NAV_ITEMS[0]
  collapsed: boolean
  pathname: string
}) {
  const isActive = pathname === item.href || pathname.startsWith(item.href + '/')
  const Icon = item.icon

  return (
    <Link
      href={item.href}
      className={cn(
        isActive ? 'nav-item-active' : 'nav-item',
        collapsed ? 'justify-center px-2' : ''
      )}
      title={collapsed ? item.label : undefined}
    >
      <Icon className="w-5 h-5 shrink-0" />
      {!collapsed && (
        <span className="flex-1 truncate">{item.label}</span>
      )}
    </Link>
  )
}

// ─── Notification Bell ────────────────────────────────────────────────────────
function NotificationBell() {
  const { notifications, unreadCount, markAllAsRead } = useNotifications()
  const [open, setOpen] = useState(false)

  return (
    <div className="relative">
      <button
        onClick={() => { setOpen(!open); if (!open) markAllAsRead() }}
        className="relative p-2 rounded-lg text-neutral-400 hover:text-neutral-100 hover:bg-surface-2 transition-all"
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <span className="absolute top-1 right-1 w-4 h-4 bg-danger text-white text-[9px] font-bold rounded-full flex items-center justify-center">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>
      <AnimatePresence>
        {open && (
          <>
            <div className="fixed inset-0 z-30" onClick={() => setOpen(false)} />
            <motion.div
              initial={{ opacity: 0, y: 8, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 8, scale: 0.95 }}
              transition={{ duration: 0.15 }}
              className="absolute right-0 top-full mt-2 w-80 card z-40 overflow-hidden shadow-card-hover"
            >
              <div className="flex items-center justify-between px-4 py-3 border-b border-border">
                <h3 className="text-sm font-semibold text-neutral-100">Notifications</h3>
                <button onClick={() => setOpen(false)} className="text-neutral-500 hover:text-neutral-300">
                  <X className="w-4 h-4" />
                </button>
              </div>
              <div className="max-h-80 overflow-y-auto divide-y divide-border">
                {notifications.length === 0 ? (
                  <p className="px-4 py-6 text-center text-sm text-neutral-500">No notifications</p>
                ) : (
                  notifications.slice(0, 6).map((n) => (
                    <div key={n.id} className={cn('px-4 py-3 hover:bg-surface-2 transition-colors', !n.read ? 'bg-primary/5' : '')}>
                      <div className="flex items-start gap-2">
                        <div className={cn('w-1.5 h-1.5 rounded-full mt-1.5 shrink-0',
                          n.type === 'warning' ? 'bg-warning' :
                          n.type === 'danger' ? 'bg-danger' :
                          n.type === 'ai' ? 'bg-ai' :
                          n.type === 'success' ? 'bg-success' : 'bg-primary'
                        )} />
                        <div>
                          <p className="text-xs font-semibold text-neutral-200">{n.title}</p>
                          <p className="text-xs text-neutral-400 mt-0.5">{n.message}</p>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  )
}

// ─── Project Selector ─────────────────────────────────────────────────────────
function ProjectSelector() {
  const { selectedProject, setSelectedProject, setProjects } = useStore((s) => ({
    selectedProject: s.selectedProject,
    setSelectedProject: s.setSelectedProject,
    setProjects: s.setProjects,
  }))
  const [open, setOpen] = useState(false)
  const [projects, setLocalProjects] = useState(mockProjects)

  useEffect(() => {
    projectsApi.getProjects()
      .then((data) => { setLocalProjects(data); setProjects(data) })
      .catch(() => { setLocalProjects(mockProjects); setProjects(mockProjects) })
  }, [setProjects])

  const current = selectedProject ?? projects[0]

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 px-3 py-2 rounded-lg border border-border bg-surface hover:border-border-subtle hover:bg-surface-2 transition-all text-sm"
      >
        <div className="w-2 h-2 rounded-full bg-success animate-pulse" />
        <span className="text-neutral-200 font-medium max-w-[160px] truncate">
          {current?.name ?? 'Select Project'}
        </span>
        <ChevronDown className="w-4 h-4 text-neutral-400" />
      </button>
      <AnimatePresence>
        {open && (
          <>
            <div className="fixed inset-0 z-30" onClick={() => setOpen(false)} />
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 8 }}
              transition={{ duration: 0.15 }}
              className="absolute left-0 top-full mt-2 w-72 card z-40 overflow-hidden shadow-card-hover"
            >
              <div className="px-3 py-2 border-b border-border">
                <p className="text-xs text-neutral-500 uppercase tracking-wider font-medium">Active Projects</p>
              </div>
              {projects.map((proj) => (
                <button
                  key={proj.id}
                  onClick={() => { setSelectedProject(proj); setOpen(false) }}
                  className={cn(
                    'w-full px-3 py-3 text-left hover:bg-surface-2 transition-colors',
                    current?.id === proj.id ? 'bg-primary/10' : ''
                  )}
                >
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-neutral-200 truncate">{proj.name}</p>
                    {current?.id === proj.id && <div className="w-2 h-2 rounded-full bg-primary shrink-0" />}
                  </div>
                  <p className="text-xs text-neutral-500 mt-0.5 truncate">{proj.client}</p>
                  <div className="flex gap-3 mt-1.5">
                    <span className="text-xs text-neutral-400">SPI: <span className={cn('font-mono font-semibold', proj.spi >= 0.9 ? 'text-success' : proj.spi >= 0.7 ? 'text-warning' : 'text-danger')}>{proj.spi.toFixed(2)}</span></span>
                    <span className="text-xs text-neutral-400">Progress: <span className="font-mono font-semibold text-neutral-200">{proj.progress}%</span></span>
                  </div>
                </button>
              ))}
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  )
}

// ─── User Menu ────────────────────────────────────────────────────────────────
function UserMenu() {
  const { user, clearAuth } = useAuth()
  const router = useRouter()
  const [open, setOpen] = useState(false)

  const handleLogout = () => {
    clearAuth()
    router.push('/login')
  }

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-surface-2 transition-all"
      >
        <div className="w-8 h-8 rounded-lg bg-gradient-primary flex items-center justify-center text-white text-sm font-bold">
          {user?.full_name?.[0] ?? 'U'}
        </div>
        <div className="hidden sm:block text-left">
          <p className="text-xs font-semibold text-neutral-200 leading-none">{user?.full_name ?? 'User'}</p>
          <p className="text-xs text-neutral-500 mt-0.5 capitalize">{user?.role ?? 'viewer'}</p>
        </div>
        <ChevronDown className="w-3.5 h-3.5 text-neutral-400 hidden sm:block" />
      </button>
      <AnimatePresence>
        {open && (
          <>
            <div className="fixed inset-0 z-30" onClick={() => setOpen(false)} />
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 8 }}
              className="absolute right-0 top-full mt-2 w-52 card z-40 overflow-hidden shadow-card-hover"
            >
              <div className="px-4 py-3 border-b border-border">
                <p className="text-sm font-semibold text-neutral-100">{user?.full_name}</p>
                <p className="text-xs text-neutral-500">{user?.email}</p>
              </div>
              <div className="py-1">
                <button className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-neutral-300 hover:bg-surface-2 hover:text-neutral-100 transition-colors">
                  <User className="w-4 h-4" /> Profile Settings
                </button>
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-danger hover:bg-danger/10 transition-colors"
                >
                  <LogOut className="w-4 h-4" /> Sign Out
                </button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  )
}

// ─── App Layout ───────────────────────────────────────────────────────────────
export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const pathname = usePathname()
  const { isAuthenticated } = useAuth()
  const { collapsed, toggle } = useSidebar()
  const [mobileOpen, setMobileOpen] = useState(false)

  useEffect(() => {
    if (!isAuthenticated) router.replace('/login')
  }, [isAuthenticated, router])

  if (!isAuthenticated) return null

  const sidebarContent = (
    <div className="flex flex-col h-full">
      {/* Logo */}
      <div className={cn('flex items-center gap-3 px-4 py-5 border-b border-border', collapsed ? 'justify-center' : '')}>
        <div className="w-8 h-8 rounded-lg bg-gradient-primary flex items-center justify-center shadow-glow-primary shrink-0">
          <Zap className="w-4 h-4 text-white" />
        </div>
        {!collapsed && (
          <div>
            <h1 className="text-sm font-bold text-neutral-100 leading-none">NEXUS PM</h1>
            <p className="text-[10px] text-primary/60 font-medium tracking-widest uppercase mt-0.5">AI Intelligence</p>
          </div>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map((item) => (
          <NavItem key={item.href} item={item} collapsed={collapsed} pathname={pathname} />
        ))}
      </nav>

      {/* Collapse toggle */}
      <div className="px-3 py-3 border-t border-border">
        <button
          onClick={toggle}
          className="w-full flex items-center justify-center gap-2 py-2 rounded-lg text-neutral-500 hover:text-neutral-300 hover:bg-surface-2 transition-all text-xs"
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <><ChevronLeft className="w-4 h-4" /><span>Collapse</span></>}
        </button>
      </div>
    </div>
  )

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* ── Desktop Sidebar ─────────────────────────────────────────────────── */}
      <motion.aside
        animate={{ width: collapsed ? 64 : 240 }}
        transition={{ duration: 0.2, ease: 'easeInOut' }}
        className="hidden lg:flex flex-col bg-surface border-r border-border shrink-0 z-20"
      >
        {sidebarContent}
      </motion.aside>

      {/* ── Mobile Sidebar ───────────────────────────────────────────────────── */}
      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/60 z-40 lg:hidden"
              onClick={() => setMobileOpen(false)}
            />
            <motion.aside
              initial={{ x: -240 }} animate={{ x: 0 }} exit={{ x: -240 }}
              transition={{ duration: 0.2 }}
              className="fixed left-0 top-0 bottom-0 w-60 bg-surface border-r border-border z-50 lg:hidden"
            >
              {sidebarContent}
            </motion.aside>
          </>
        )}
      </AnimatePresence>

      {/* ── Main Area ───────────────────────────────────────────────────────── */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Bar */}
        <header className="flex items-center justify-between px-4 py-3 bg-surface border-b border-border shrink-0 z-10">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setMobileOpen(true)}
              className="lg:hidden p-2 rounded-lg text-neutral-400 hover:text-neutral-100 hover:bg-surface-2 transition-all"
            >
              <Menu className="w-5 h-5" />
            </button>
            <ProjectSelector />
          </div>
          <div className="flex items-center gap-2">
            <NotificationBell />
            <div className="w-px h-6 bg-border mx-1" />
            <UserMenu />
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto page-transition">
          {children}
        </main>
      </div>
    </div>
  )
}
