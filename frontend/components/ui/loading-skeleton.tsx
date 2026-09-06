import { cn } from '@/lib/utils'

// ─── Skeleton Base ────────────────────────────────────────────────────────────
interface SkeletonProps {
  className?: string
}

export function Skeleton({ className }: SkeletonProps) {
  return <div className={cn('skeleton rounded', className)} aria-hidden="true" />
}

// ─── Stats Card Skeleton ──────────────────────────────────────────────────────
export function StatsCardSkeleton() {
  return (
    <div className="card p-5 space-y-3" aria-busy="true" aria-label="Loading...">
      <div className="flex items-center justify-between">
        <Skeleton className="h-3 w-24" />
        <Skeleton className="h-8 w-8 rounded-lg" />
      </div>
      <Skeleton className="h-8 w-28" />
      <Skeleton className="h-3 w-20" />
    </div>
  )
}

// ─── Table Skeleton ───────────────────────────────────────────────────────────
interface TableSkeletonProps {
  rows?: number
  columns?: number
}

export function TableSkeleton({ rows = 5, columns = 5 }: TableSkeletonProps) {
  return (
    <div className="card overflow-hidden" aria-busy="true">
      {/* Header */}
      <div className="flex gap-4 px-4 py-3 border-b border-border bg-surface">
        {Array.from({ length: columns }).map((_, i) => (
          <Skeleton key={i} className="h-3 flex-1" />
        ))}
      </div>
      {/* Rows */}
      {Array.from({ length: rows }).map((_, row) => (
        <div
          key={row}
          className="flex gap-4 px-4 py-3 border-b border-border last:border-0"
        >
          {Array.from({ length: columns }).map((_, col) => (
            <Skeleton
              key={col}
              className={cn('h-3 flex-1', col === 0 ? 'max-w-[140px]' : '')}
            />
          ))}
        </div>
      ))}
    </div>
  )
}

// ─── Chat Message Skeleton ────────────────────────────────────────────────────
export function ChatSkeleton() {
  return (
    <div className="flex items-start gap-3 p-4" aria-busy="true">
      <Skeleton className="h-8 w-8 rounded-full shrink-0" />
      <div className="flex-1 space-y-2">
        <Skeleton className="h-3 w-3/4" />
        <Skeleton className="h-3 w-1/2" />
        <Skeleton className="h-3 w-2/3" />
      </div>
    </div>
  )
}

// ─── Card Skeleton ────────────────────────────────────────────────────────────
export function CardSkeleton({ lines = 3 }: { lines?: number }) {
  return (
    <div className="card p-4 space-y-3" aria-busy="true">
      <div className="flex items-center gap-3">
        <Skeleton className="h-10 w-10 rounded-lg shrink-0" />
        <div className="flex-1 space-y-2">
          <Skeleton className="h-3 w-32" />
          <Skeleton className="h-2 w-20" />
        </div>
      </div>
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton key={i} className={cn('h-2.5', i === lines - 1 ? 'w-3/4' : 'w-full')} />
      ))}
    </div>
  )
}

// ─── Full-page Loading ────────────────────────────────────────────────────────
export function PageLoading() {
  return (
    <div className="flex items-center justify-center h-64 flex-col gap-4">
      <div className="relative">
        <div className="w-12 h-12 border-2 border-border rounded-full animate-spin border-t-primary" />
        <div className="absolute inset-0 w-12 h-12 border-2 border-transparent border-b-ai rounded-full animate-spin" style={{ animationDuration: '1.5s', animationDirection: 'reverse' }} />
      </div>
      <p className="text-neutral-400 text-sm">Loading...</p>
    </div>
  )
}

// ─── Animated Dots (chat typing indicator) ────────────────────────────────────
export function TypingDots() {
  return (
    <div className="flex items-center gap-1 py-1 px-2" aria-label="Loading response...">
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className="w-2 h-2 bg-ai rounded-full animate-bounce"
          style={{ animationDelay: `${i * 0.15}s` }}
        />
      ))}
    </div>
  )
}
