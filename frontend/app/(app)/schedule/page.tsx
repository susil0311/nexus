'use client'

import { useState } from 'react'
import {
  Calendar as CalendarIcon, Filter, Layers, CheckCircle2,
  Clock, AlertCircle, ChevronDown, ChevronRight
} from 'lucide-react'
import { mockSchedule } from '@/lib/mock-data'
import { ScheduleActivity } from '@/lib/api'
import { StatusBadge } from '@/components/ui/status-badge'

export default function SchedulePage() {
  const [activities] = useState<ScheduleActivity[]>(mockSchedule)
  const [disciplineFilter, setDisciplineFilter] = useState<string>('all')
  const [expandedNodes, setExpandedNodes] = useState<Record<string, boolean>>({
    'L1-01': true,
    'L2-01': true,
  })

  const toggleExpand = (id: string) => {
    setExpandedNodes((prev) => ({ ...prev, [id]: !prev[id] }))
  }

  const filtered = activities.filter((act) => {
    if (disciplineFilter === 'all') return true
    return act.discipline.toLowerCase() === disciplineFilter.toLowerCase()
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-surface border border-border rounded-xl p-5">
        <div>
          <div className="flex items-center gap-2">
            <CalendarIcon className="w-5 h-5 text-primary" />
            <h1 className="text-xl font-bold text-white">L1-L6 Project Schedule Tree</h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-400 font-mono border border-blue-500/20">
              PRIMAVERA P6 / MS PROJECT COMPATIBLE
            </span>
          </div>
          <p className="text-sm text-text-muted mt-1">
            Hierarchical WBS schedule view with overlay of AI-extracted field actuals and float consumption
          </p>
        </div>

        {/* Filter Tabs */}
        <div className="flex bg-surface-card p-1 rounded-lg border border-border">
          {['all', 'Civil', 'Piping', 'Electrical', 'Instrumentation'].map((disc) => (
            <button
              key={disc}
              onClick={() => setDisciplineFilter(disc)}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                disciplineFilter.toLowerCase() === disc.toLowerCase()
                  ? 'bg-surface border border-border text-white'
                  : 'text-text-muted hover:text-white'
              }`}
            >
              {disc === 'all' ? 'All Disciplines' : disc}
            </button>
          ))}
        </div>
      </div>

      {/* Gantt & Schedule Table */}
      <div className="bg-surface border border-border rounded-xl overflow-hidden shadow-sm">
        <div className="p-4 border-b border-border flex items-center justify-between text-xs text-text-muted font-medium bg-surface-card">
          <div className="w-2/5">Activity / WBS Description</div>
          <div className="w-1/6 text-center">Baseline Dates</div>
          <div className="w-1/6 text-center">Actual Progress</div>
          <div className="w-1/12 text-center">Float</div>
          <div className="w-1/6 text-right">Status</div>
        </div>

        <div className="divide-y divide-border/60">
          {filtered.map((act) => {
            const isL1 = act.level === 1
            const isL2 = act.level === 2
            const isL5 = act.level === 5
            const isExpanded = expandedNodes[act.id] ?? true

            return (
              <div
                key={act.id}
                className={`flex items-center p-3.5 hover:bg-surface-card/60 transition-colors text-xs ${
                  isL1 ? 'bg-surface-card font-semibold' : ''
                }`}
              >
                {/* Name & Indentation */}
                <div
                  className="w-2/5 flex items-center gap-2"
                  style={{ paddingLeft: `${(act.level - 1) * 18}px` }}
                >
                  {!isL5 ? (
                    <button
                      onClick={() => toggleExpand(act.id)}
                      className="p-0.5 hover:bg-surface-elevated rounded text-text-muted hover:text-white"
                    >
                      {isExpanded ? (
                        <ChevronDown className="w-3.5 h-3.5" />
                      ) : (
                        <ChevronRight className="w-3.5 h-3.5" />
                      )}
                    </button>
                  ) : (
                    <span className="w-3.5 h-3.5" />
                  )}

                  <span className="font-mono text-[11px] text-primary/80 shrink-0">
                    {act.activity_id || act.wbs_code}
                  </span>
                  <span className={`truncate ${isL1 || isL2 ? 'text-white font-medium' : 'text-text-secondary'}`}>
                    {act.name}
                  </span>
                </div>

                {/* Baseline Dates */}
                <div className="w-1/6 text-center font-mono text-[11px] text-text-muted">
                  {act.planned_start} → {act.planned_finish}
                </div>

                {/* Progress Bar */}
                <div className="w-1/6 px-4">
                  <div className="flex items-center justify-between text-[10px] font-mono text-text-muted mb-1">
                    <span>{act.actual_progress ?? act.progress}%</span>
                    <span>{act.planned_progress ?? act.progress}% plan</span>
                  </div>
                  <div className="w-full bg-surface-elevated rounded-full h-1.5 overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-300 ${
                        (act.actual_progress ?? act.progress) >= (act.planned_progress ?? act.progress) ? 'bg-emerald-400' : 'bg-amber-400'
                      }`}
                      style={{ width: `${act.actual_progress ?? act.progress}%` }}
                    />
                  </div>
                </div>

                {/* Float Days */}
                <div className="w-1/12 text-center font-mono text-xs">
                  <span
                    className={
                      act.float_days <= 0
                        ? 'text-red-400 font-bold'
                        : act.float_days <= 3
                        ? 'text-amber-400'
                        : 'text-text-muted'
                    }
                  >
                    {act.float_days}d
                  </span>
                </div>

                {/* Status Badge */}
                <div className="w-1/6 flex justify-end">
                  <StatusBadge
                    status={
                      act.status === 'completed'
                        ? 'success'
                        : act.status === 'delayed'
                        ? 'danger'
                        : act.status === 'in_progress'
                        ? 'info'
                        : 'default'
                    }
                    label={act.status.replace('_', ' ')}
                    size="sm"
                  />
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
