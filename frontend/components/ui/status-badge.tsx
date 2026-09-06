import { cn } from '@/lib/utils'
import { cva, type VariantProps } from 'class-variance-authority'

const badgeVariants = cva(
  'inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold transition-colors',
  {
    variants: {
      variant: {
        success: 'bg-success/15 text-success border border-success/30',
        warning: 'bg-warning/15 text-warning border border-warning/30',
        danger: 'bg-danger/15 text-danger border border-danger/30',
        info: 'bg-primary/15 text-primary border border-primary/30',
        ai: 'bg-ai/15 text-ai border border-ai/30',
        neutral: 'bg-neutral-700/50 text-neutral-300 border border-neutral-600/30',
        outline: 'bg-transparent text-neutral-300 border border-neutral-600',
      },
    },
    defaultVariants: {
      variant: 'neutral',
    },
  }
)

interface StatusBadgeProps extends VariantProps<typeof badgeVariants> {
  children?: React.ReactNode
  status?: string
  label?: string
  size?: 'sm' | 'md'
  dot?: boolean
  className?: string
}

const dotColor: Record<string, string> = {
  success: 'bg-success',
  warning: 'bg-warning',
  danger: 'bg-danger',
  info: 'bg-primary',
  ai: 'bg-ai',
  neutral: 'bg-neutral-400',
  outline: 'bg-neutral-400',
}

export function StatusBadge({
  children,
  status,
  label,
  size = 'md',
  variant,
  dot = false,
  className
}: StatusBadgeProps) {
  const resolvedVariant = variant || (status ? getStatusVariant(status) : 'neutral')
  const content = children || label || status

  return (
    <span
      className={cn(
        badgeVariants({ variant: resolvedVariant }),
        size === 'sm' ? 'px-2 py-0.5 text-[10px]' : '',
        className
      )}
    >
      {dot && (
        <span
          className={cn('w-1.5 h-1.5 rounded-full', dotColor[resolvedVariant ?? 'neutral'])}
          aria-hidden="true"
        />
      )}
      {content}
    </span>
  )
}

// Convenience helpers
export function getStatusVariant(
  status: string
): 'success' | 'warning' | 'danger' | 'info' | 'neutral' {
  switch (status) {
    case 'on_track':
    case 'completed':
    case 'done':
    case 'approved':
    case 'resolved':
      return 'success'
    case 'at_risk':
    case 'processing':
    case 'pending':
    case 'investigating':
    case 'medium':
      return 'warning'
    case 'delayed':
    case 'failed':
    case 'rejected':
    case 'critical':
      return 'danger'
    case 'info':
    case 'not_started':
      return 'info'
    default:
      return 'neutral'
  }
}
