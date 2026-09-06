import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(dateStr: string, opts?: Intl.DateTimeFormatOptions): string {
  try {
    return new Date(dateStr).toLocaleDateString('en-IN', {
      day: '2-digit', month: 'short', year: 'numeric',
      ...opts,
    })
  } catch {
    return dateStr
  }
}

export function formatRelativeTime(dateStr: string): string {
  const now = Date.now()
  const then = new Date(dateStr).getTime()
  const diffMs = now - then
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  return `${diffDays}d ago`
}

export function getConfidenceColor(score: number): string {
  if (score >= 0.85) return 'text-success'
  if (score >= 0.5) return 'text-warning'
  return 'text-danger'
}

export function getConfidenceBg(score: number): string {
  if (score >= 0.85) return 'bg-success'
  if (score >= 0.5) return 'bg-warning'
  return 'bg-danger'
}

export function getStatusColor(status: string): string {
  switch (status) {
    case 'on_track': case 'completed': case 'done': case 'approved': return 'text-success'
    case 'at_risk': case 'processing': case 'pending': return 'text-warning'
    case 'delayed': case 'failed': case 'rejected': return 'text-danger'
    case 'not_started': return 'text-neutral-400'
    default: return 'text-neutral-400'
  }
}

export function formatPercent(val: number, digits = 0): string {
  return `${(val * 100).toFixed(digits)}%`
}

export function clamp(val: number, min: number, max: number): number {
  return Math.min(Math.max(val, min), max)
}
