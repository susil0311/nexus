import { cn } from '@/lib/utils'

interface ConfidenceBarProps {
  score?: number // 0-1
  value?: number // 0-1 alias
  showLabel?: boolean
  showPercent?: boolean
  height?: 'sm' | 'md' | 'lg'
  className?: string
}

export function ConfidenceBar({
  score,
  value,
  showLabel = true,
  showPercent = true,
  height = 'sm',
  className,
}: ConfidenceBarProps) {
  const actualScore = score !== undefined ? score : (value ?? 0)
  const percent = Math.round(actualScore * 100)

  const barColor =
    actualScore >= 0.85
      ? 'bg-success'
      : actualScore >= 0.5
      ? 'bg-warning'
      : 'bg-danger'

  const labelColor =
    actualScore >= 0.85
      ? 'text-success'
      : actualScore >= 0.5
      ? 'text-warning'
      : 'text-danger'

  const label =
    actualScore >= 0.85 ? 'High' : actualScore >= 0.5 ? 'Medium' : 'Low'

  const heightClass = {
    sm: 'h-1.5',
    md: 'h-2.5',
    lg: 'h-3',
  }[height]

  return (
    <div className={cn('w-full', className)}>
      {(showLabel || showPercent) && (
        <div className="flex items-center justify-between mb-1">
          {showLabel && (
            <span className={cn('text-xs font-medium', labelColor)}>{label}</span>
          )}
          {showPercent && (
            <span className={cn('text-xs font-mono font-semibold', labelColor)}>
              {percent}%
            </span>
          )}
        </div>
      )}
      <div className={cn('w-full bg-neutral-800 rounded-full overflow-hidden', heightClass)}>
        <div
          className={cn('h-full rounded-full transition-all duration-500', barColor)}
          style={{ width: `${percent}%` }}
          role="progressbar"
          aria-valuenow={percent}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label={`Confidence: ${percent}%`}
        />
      </div>
    </div>
  )
}
