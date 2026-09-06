import { cn } from '@/lib/utils'
import { cva, type VariantProps } from 'class-variance-authority'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

const cardVariants = cva('card p-5 flex flex-col gap-3', {
  variants: {
    variant: {
      default: '',
      primary: 'border-primary/30 bg-primary/5',
      success: 'border-success/30 bg-success/5',
      warning: 'border-warning/30 bg-warning/5',
      danger: 'border-danger/30 bg-danger/5',
      ai: 'border-ai/30 bg-ai/5',
    },
  },
  defaultVariants: { variant: 'default' },
})

const iconBg: Record<string, string> = {
  default: 'bg-neutral-700/50 text-neutral-300',
  primary: 'bg-primary/20 text-primary',
  success: 'bg-success/20 text-success',
  warning: 'bg-warning/20 text-warning',
  danger: 'bg-danger/20 text-danger',
  ai: 'bg-ai/20 text-ai',
}

interface StatsCardProps extends VariantProps<typeof cardVariants> {
  title: string
  value: string | number
  unit?: string
  trend?: number | { value: string; direction: 'up' | 'down'; label?: string }
  trendInverse?: boolean
  icon?: React.ReactNode | React.ComponentType<{ className?: string }>
  subtitle?: string
  className?: string
  onClick?: () => void
}

export function StatsCard({
  title,
  value,
  unit,
  trend,
  trendInverse = false,
  icon,
  subtitle,
  variant = 'default',
  className,
  onClick,
}: StatsCardProps) {
  const isNumericTrend = typeof trend === 'number'
  const isPositiveTrend = isNumericTrend && trend > 0
  const isNegativeTrend = isNumericTrend && trend < 0
  const isGoodTrend = trendInverse ? isNegativeTrend : isPositiveTrend
  const isBadTrend = trendInverse ? isPositiveTrend : isNegativeTrend

  const IconComponent = typeof icon === 'function' ? icon : null

  return (
    <div
      className={cn(
        cardVariants({ variant }),
        onClick ? 'cursor-pointer transition-all hover:border-border-subtle hover:shadow-card-hover' : '',
        className
      )}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
    >
      {/* Header row */}
      <div className="flex items-start justify-between">
        <span className="text-xs font-medium text-neutral-400 uppercase tracking-wider">{title}</span>
        {icon && (
          <span className={cn('p-2 rounded-lg text-lg flex items-center justify-center', iconBg[variant ?? 'default'])}>
            {typeof icon === 'function' ? (
              (() => {
                const Comp = icon as React.ComponentType<{ className?: string }>
                return <Comp className="w-5 h-5" />
              })()
            ) : (
              (icon as React.ReactNode)
            )}
          </span>
        )}
      </div>

      {/* Value */}
      <div className="flex items-baseline gap-1.5">
        <span className="text-3xl font-bold text-neutral-100 font-mono tracking-tight leading-none">
          {value}
        </span>
        {unit && <span className="text-sm text-neutral-400 font-medium">{unit}</span>}
      </div>

      {/* Trend + Subtitle */}
      <div className="flex items-center gap-2">
        {trend !== undefined && (
          typeof trend === 'object' ? (
            <span
              className={cn(
                'flex items-center gap-0.5 text-xs font-semibold',
                trend.direction === 'up' ? 'text-success' : 'text-danger'
              )}
            >
              {trend.direction === 'up' ? (
                <TrendingUp className="w-3 h-3" />
              ) : (
                <TrendingDown className="w-3 h-3" />
              )}
              {trend.value} {trend.label ? <span className="text-neutral-500 font-normal ml-1">{trend.label}</span> : ''}
            </span>
          ) : (
            <span
              className={cn(
                'flex items-center gap-0.5 text-xs font-semibold',
                isGoodTrend ? 'text-success' : isBadTrend ? 'text-danger' : 'text-neutral-400'
              )}
            >
              {isPositiveTrend ? (
                <TrendingUp className="w-3 h-3" />
              ) : isNegativeTrend ? (
                <TrendingDown className="w-3 h-3" />
              ) : (
                <Minus className="w-3 h-3" />
              )}
              {trend > 0 ? '+' : ''}{(trend * 100).toFixed(1)}%
            </span>
          )
        )}
        {subtitle && (
          <span className="text-xs text-neutral-500">{subtitle}</span>
        )}
      </div>
    </div>
  )
}
