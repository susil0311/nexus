'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  TrendingUp, TrendingDown, Clock, AlertTriangle, CheckCircle2,
  Calendar, Layers, Activity, ArrowUpRight, ArrowDownRight, RefreshCw
} from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { analyticsApi, DashboardData } from '@/lib/api'
import { mockDashboard } from '@/lib/mock-data'
import { useStore } from '@/lib/store'
import { StatsCard } from '@/components/ui/stats-card'
import { StatusBadge } from '@/components/ui/status-badge'
import { ConfidenceBar } from '@/components/ui/confidence-bar'

export default function DashboardPage() {
  const selectedProject = useStore((s) => s.selectedProject)
  const [activeTab, setActiveTab] = useState<'all' | 'piping' | 'civil' | 'electrical'>('all')

  const { data: dashboard = mockDashboard, isLoading, refetch } = useQuery<DashboardData>({
    queryKey: ['dashboard', selectedProject?.id],
    queryFn: async () => {
      try {
        if (!selectedProject?.id) return mockDashboard
        return await analyticsApi.getDashboard(selectedProject.id)
      } catch (err) {
        return mockDashboard
      }
    },
  })

  return (
    <div className="space-y-6">
      {/* Top Welcome Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-surface border border-border rounded-xl p-5 shadow-sm">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
            <h1 className="text-xl font-bold text-white tracking-wide">Command Center</h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-400 font-mono border border-blue-500/20">
              OIL INDIA LIMITED · LIVE PMIS
            </span>
          </div>
          <p className="text-sm text-text-muted mt-1">
            Real-time planning vs execution telemetry with automated L5/L6 reconciliation
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => refetch()}
            className="flex items-center gap-2 px-3.5 py-2 text-xs font-medium rounded-lg bg-surface-card border border-border hover:border-border-active text-text-secondary transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            Sync Now
          </button>
          <div className="text-xs font-mono text-text-muted bg-surface-card px-3 py-2 rounded-lg border border-border">
            Last update: <span className="text-emerald-400">Just now</span>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="Schedule Performance (SPI)"
          value={dashboard.spi.toFixed(2)}
          subtitle={dashboard.spi >= 1.0 ? 'Ahead of baseline' : 'Behind planned pace'}
          trend={{
            value: `${(dashboard.spi_trend * 100).toFixed(1)}%`,
            direction: dashboard.spi_trend >= 0 ? 'up' : 'down',
            label: 'vs last week'
          }}
          icon={Activity}
          variant={dashboard.spi >= 0.95 ? 'success' : dashboard.spi >= 0.85 ? 'warning' : 'danger'}
        />

        <StatsCard
          title="Cost Performance (CPI)"
          value={dashboard.cpi.toFixed(2)}
          subtitle="Earned vs Actual cost"
          trend={{
            value: `${(dashboard.cpi_trend * 100).toFixed(1)}%`,
            direction: dashboard.cpi_trend >= 0 ? 'up' : 'down',
            label: 'earned value'
          }}
          icon={TrendingUp}
          variant={dashboard.cpi >= 1.0 ? 'success' : 'warning'}
        />

        <StatsCard
          title="Activity Completion"
          value={`${dashboard.completed_activities}/${dashboard.total_activities}`}
          subtitle={`${Math.round((dashboard.completed_activities / dashboard.total_activities) * 100)}% WBS nodes closed`}
          icon={CheckCircle2}
          variant="primary"
        />

        <StatsCard
          title="Bottlenecks & At Risk"
          value={dashboard.at_risk_count.toString()}
          subtitle={`${dashboard.delayed_count} critical path delay`}
          icon={AlertTriangle}
          variant={dashboard.at_risk_count > 10 ? 'danger' : 'warning'}
        />
      </div>

      {/* S-Curve & Progress Flow */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Planned vs Actual S-Curve Simulation */}
        <div className="lg:col-span-2 bg-surface border border-border rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-semibold text-white">Execution S-Curve Telemetry</h2>
              <p className="text-xs text-text-muted">Cumulative planned vs validated actual progress %</p>
            </div>
            <div className="flex items-center gap-3 text-xs">
              <span className="flex items-center gap-1.5 text-text-secondary">
                <span className="w-3 h-0.5 bg-blue-500 rounded" /> Planned Baseline
              </span>
              <span className="flex items-center gap-1.5 text-emerald-400">
                <span className="w-3 h-0.5 bg-emerald-500 rounded" /> Field Actuals
              </span>
            </div>
          </div>

          <div className="h-64 flex flex-col justify-end gap-3 pt-6">
            <div className="grid grid-cols-6 gap-3 h-48 items-end border-b border-border/80 pb-2">
              {[
                { label: 'Week 1', planned: 20, actual: 20 },
                { label: 'Week 2', planned: 35, actual: 33 },
                { label: 'Week 3', planned: 48, actual: 44 },
                { label: 'Week 4', planned: 62, actual: 56 },
                { label: 'Week 5', planned: 78, actual: 69 },
                { label: 'Current', planned: 90, actual: 78 }
              ].map((point, idx) => (
                <div key={idx} className="flex flex-col items-center gap-2 h-full justify-end group">
                  <div className="w-full flex items-end justify-center gap-1.5 h-full">
                    {/* Planned Bar */}
                    <div
                      style={{ height: `${point.planned}%` }}
                      className="w-4 bg-blue-500/30 border-t-2 border-blue-400 rounded-t transition-all"
                      title={`Planned: ${point.planned}%`}
                    />
                    {/* Actual Bar */}
                    <div
                      style={{ height: `${point.actual}%` }}
                      className="w-4 bg-emerald-500/70 border-t-2 border-emerald-400 rounded-t transition-all"
                      title={`Actual: ${point.actual}%`}
                    />
                  </div>
                  <span className="text-[11px] font-mono text-text-muted group-hover:text-white transition-colors">
                    {point.label}
                  </span>
                </div>
              ))}
            </div>
            <div className="flex justify-between items-center text-xs text-text-muted px-1">
              <span>Sprint Lag: <strong className="text-amber-400 font-mono">12% Variance</strong></span>
              <span className="text-ai-accent flex items-center gap-1">
                <Activity className="w-3.5 h-3.5" /> Delay Oracle: Early warning active
              </span>
            </div>
          </div>
        </div>

        {/* Real-time Submissions Feed */}
        <div className="bg-surface border border-border rounded-xl p-5 flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-semibold text-white">Live Ingestion Stream</h2>
              <p className="text-xs text-text-muted">Field voice, text & daily spreadsheets</p>
            </div>
            <span className="text-[10px] bg-surface-card px-2 py-0.5 rounded text-emerald-400 border border-emerald-500/30">
              STREAMING
            </span>
          </div>

          <div className="space-y-3 overflow-y-auto max-h-[290px] pr-1">
            {dashboard.recent_submissions.map((sub) => (
              <div
                key={sub.id}
                className="p-3 rounded-lg bg-surface-card border border-border hover:border-border-active transition-all"
              >
                <div className="flex items-start justify-between gap-2">
                  <span className="text-xs font-semibold text-white leading-tight">
                    {sub.description}
                  </span>
                  <StatusBadge
                    status={sub.status === 'done' ? 'success' : sub.status === 'processing' ? 'warning' : 'danger'}
                    size="sm"
                  />
                </div>
                <div className="mt-2 flex items-center justify-between text-[11px] text-text-muted">
                  <span className="text-blue-400 font-mono">{sub.discipline}</span>
                  <span>{sub.submitted_by}</span>
                </div>
                {sub.matched_activity && (
                  <div className="mt-2 pt-2 border-t border-border/50 flex items-center justify-between text-[10px] font-mono">
                    <span className="text-text-muted">Node: <span className="text-white">{sub.matched_activity}</span></span>
                    {sub.confidence && (
                      <span className="text-emerald-400">{(sub.confidence * 100).toFixed(0)}% match</span>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Discipline Progress Breakdown */}
      <div className="bg-surface border border-border rounded-xl p-5">
        <h2 className="text-base font-semibold text-white mb-1">Discipline-Wise Execution Progress</h2>
        <p className="text-xs text-text-muted mb-4">Granular L5/L6 tracking across parallel engineering departments</p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {dashboard.discipline_breakdown.map((item) => {
            const pct = Math.round((item.completed / item.total) * 100)
            return (
              <div key={item.discipline} className="p-4 rounded-lg bg-surface-card border border-border">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-semibold text-white">{item.discipline}</span>
                  <span className="text-xs font-mono text-emerald-400">{pct}%</span>
                </div>
                <div className="w-full bg-surface-elevated rounded-full h-2 overflow-hidden mb-3">
                  <div
                    className="bg-blue-500 h-full rounded-full transition-all duration-500"
                    style={{ width: `${pct}%` }}
                  />
                </div>
                <div className="flex justify-between text-[11px] text-text-muted">
                  <span>Completed: <strong className="text-white font-mono">{item.completed}</strong></span>
                  <span>At Risk: <strong className="text-amber-400 font-mono">{item.at_risk}</strong></span>
                  <span>Delayed: <strong className="text-red-400 font-mono">{item.delayed}</strong></span>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
