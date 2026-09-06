'use client'

import { useState } from 'react'
import {
  AlertTriangle, ShieldCheck, CheckCircle2, Clock,
  Filter, Search, ArrowRight, Eye, ChevronRight
} from 'lucide-react'
import toast from 'react-hot-toast'
import { mockAnomalies } from '@/lib/mock-data'
import { Anomaly } from '@/lib/api'
import { StatusBadge } from '@/components/ui/status-badge'

export default function AnomaliesPage() {
  const [anomalies, setAnomalies] = useState<Anomaly[]>(mockAnomalies)
  const [filterSeverity, setFilterSeverity] = useState<string>('all')

  const handleResolve = (id: string) => {
    setAnomalies((prev) =>
      prev.map((a) => (a.id === id ? { ...a, status: 'resolved' } : a))
    )
    toast.success('Anomaly flagged as resolved after field verification')
  }

  const filtered = anomalies.filter((a) => {
    if (filterSeverity === 'all') return true
    return a.severity === filterSeverity
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-surface border border-border rounded-xl p-5">
        <div>
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-400" />
            <h1 className="text-xl font-bold text-white">Anomaly Sentinel — Data Governance</h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-red-500/10 text-red-400 font-mono border border-red-500/20">
              ISOLATION FOREST + 6 RULE CHECKS
            </span>
          </div>
          <p className="text-sm text-text-muted mt-1">
            Autonomous data integrity watchdog flagging overclaimed progress, ghost shifts, and temporal contradictions
          </p>
        </div>

        {/* Severity Filters */}
        <div className="flex bg-surface-card p-1 rounded-lg border border-border">
          {['all', 'critical', 'medium', 'low'].map((sev) => (
            <button
              key={sev}
              onClick={() => setFilterSeverity(sev)}
              className={`px-3 py-1.5 text-xs font-medium rounded-md capitalize transition-colors ${
                filterSeverity === sev
                  ? 'bg-surface border border-border text-white'
                  : 'text-text-muted hover:text-white'
              }`}
            >
              {sev}
            </button>
          ))}
        </div>
      </div>

      {/* Anomaly Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filtered.map((anomaly) => {
          const isResolved = anomaly.status === 'resolved'
          return (
            <div
              key={anomaly.id}
              className={`p-5 rounded-xl border space-y-3 transition-all ${
                isResolved
                  ? 'bg-surface/50 border-border/40 opacity-75'
                  : anomaly.severity === 'critical'
                  ? 'bg-surface border-red-500/40 ring-1 ring-red-500/10'
                  : 'bg-surface border-amber-500/40'
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span
                    className={`w-2 h-2 rounded-full ${
                      isResolved
                        ? 'bg-emerald-400'
                        : anomaly.severity === 'critical'
                        ? 'bg-red-400 animate-pulse'
                        : 'bg-amber-400'
                    }`}
                  />
                  <h3 className="text-sm font-semibold text-white">{anomaly.title}</h3>
                </div>
                <StatusBadge
                  status={
                    isResolved
                      ? 'success'
                      : anomaly.severity === 'critical'
                      ? 'danger'
                      : 'warning'
                  }
                  label={isResolved ? 'Resolved' : anomaly.severity}
                  size="sm"
                />
              </div>

              <p className="text-xs text-text-secondary leading-relaxed">
                {anomaly.description}
              </p>

              <div className="p-3 rounded-lg bg-surface-card border border-border text-[11px] flex justify-between items-center font-mono text-text-muted">
                <span>Related Node: <strong className="text-white">{anomaly.related_activity_id || 'N/A'}</strong></span>
                <span>Detected: {anomaly.detected_at}</span>
              </div>

              <div className="pt-2 flex justify-end gap-2">
                {!isResolved && (
                  <button
                    type="button"
                    onClick={() => handleResolve(anomaly.id)}
                    className="px-3.5 py-1.5 bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 border border-emerald-500/30 text-xs font-medium rounded-lg flex items-center gap-1.5 transition-colors"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Verify & Resolve
                  </button>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
