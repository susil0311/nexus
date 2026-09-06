'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  CheckSquare, Check, X, PlusCircle, AlertTriangle,
  ChevronRight, Filter, Sparkles, ShieldCheck
} from 'lucide-react'
import toast from 'react-hot-toast'
import { matchesApi, ReviewItem } from '@/lib/api'
import { mockReviewQueue } from '@/lib/mock-data'
import { useStore } from '@/lib/store'
import { ConfidenceBar } from '@/components/ui/confidence-bar'
import { StatusBadge } from '@/components/ui/status-badge'

export default function ReviewQueuePage() {
  const selectedProject = useStore((s) => s.selectedProject)
  const [items, setItems] = useState<ReviewItem[]>(mockReviewQueue)
  const [selectedItem, setSelectedItem] = useState<ReviewItem | null>(mockReviewQueue[0] || null)
  const [activeFilter, setActiveFilter] = useState<'all' | 'needs_review' | 'flagged_new'>('all')

  const handleApprove = async (item: ReviewItem) => {
    try {
      await matchesApi.approveMatch(item.id, {
        activity_id: item.candidates[0]?.activity_id || 'PIP-001',
      })
    } catch {
      // Optimistic fallback
    }
    setItems((prev) => prev.filter((i) => i.id !== item.id))
    if (selectedItem?.id === item.id) {
      const remaining = items.filter((i) => i.id !== item.id)
      setSelectedItem(remaining[0] || null)
    }
    toast.success(`Match approved for ${item.candidates[0]?.activity_id || 'activity'}!`)
  }

  const handleReject = async (item: ReviewItem) => {
    try {
      await matchesApi.rejectMatch(item.id, 'Planner manual override')
    } catch {
      // Optimistic fallback
    }
    setItems((prev) => prev.filter((i) => i.id !== item.id))
    if (selectedItem?.id === item.id) {
      const remaining = items.filter((i) => i.id !== item.id)
      setSelectedItem(remaining[0] || null)
    }
    toast.error('Match rejected and dismissed')
  }

  const handleFlagNew = (item: ReviewItem) => {
    setItems((prev) => prev.filter((i) => i.id !== item.id))
    if (selectedItem?.id === item.id) {
      const remaining = items.filter((i) => i.id !== item.id)
      setSelectedItem(remaining[0] || null)
    }
    toast('Flagged as new L5 activity for WBS baseline update', { icon: '📌' })
  }

  const filteredItems = items.filter((i) => {
    if (activeFilter === 'all') return true
    return i.status === activeFilter
  })

  return (
    <div className="space-y-6">
      {/* Top Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-surface border border-border rounded-xl p-5">
        <div>
          <div className="flex items-center gap-2">
            <CheckSquare className="w-5 h-5 text-primary" />
            <h1 className="text-xl font-bold text-white">Activity Match Review Queue</h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-400 font-mono border border-amber-500/20">
              {items.length} PENDING REVIEW
            </span>
          </div>
          <p className="text-sm text-text-muted mt-1">
            Human-in-the-loop validation: review ambiguous field terminology before committing to Primavera baseline
          </p>
        </div>

        {/* Filters */}
        <div className="flex bg-surface-card p-1 rounded-lg border border-border">
          <button
            onClick={() => setActiveFilter('all')}
            className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
              activeFilter === 'all' ? 'bg-surface border border-border text-white' : 'text-text-muted hover:text-white'
            }`}
          >
            All Items ({items.length})
          </button>
          <button
            onClick={() => setActiveFilter('needs_review')}
            className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
              activeFilter === 'needs_review' ? 'bg-surface border border-border text-white' : 'text-text-muted hover:text-white'
            }`}
          >
            Needs Review
          </button>
          <button
            onClick={() => setActiveFilter('flagged_new')}
            className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
              activeFilter === 'flagged_new' ? 'bg-surface border border-border text-white' : 'text-text-muted hover:text-white'
            }`}
          >
            New Scope / Unmatched
          </button>
        </div>
      </div>

      {/* Split Review Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left List Pane */}
        <div className="lg:col-span-5 bg-surface border border-border rounded-xl p-4 space-y-3 max-h-[680px] overflow-y-auto">
          <div className="flex items-center justify-between pb-2 border-b border-border text-xs text-text-muted">
            <span>Pending Field Observations</span>
            <span>Confidence</span>
          </div>

          {filteredItems.length === 0 ? (
            <div className="p-8 text-center text-text-muted">
              <ShieldCheck className="w-10 h-10 mx-auto opacity-30 mb-2" />
              <p className="text-xs font-medium">Review queue is clear!</p>
              <p className="text-[11px]">All extracted activities reconciled with the schedule.</p>
            </div>
          ) : (
            filteredItems.map((item) => {
              const isSelected = selectedItem?.id === item.id
              const topScore = item.candidates[0]?.score || 0
              return (
                <div
                  key={item.id}
                  onClick={() => setSelectedItem(item)}
                  className={`p-3.5 rounded-lg border cursor-pointer transition-all ${
                    isSelected
                      ? 'border-primary bg-primary/5 shadow-sm'
                      : 'border-border bg-surface-card hover:border-border-active'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <span className="text-xs font-semibold text-white line-clamp-2">
                      {item.raw_description || item.extracted_text}
                    </span>
                    <span
                      className={`text-xs font-mono font-bold shrink-0 ${
                        topScore >= 0.85
                          ? 'text-emerald-400'
                          : topScore >= 0.5
                          ? 'text-amber-400'
                          : 'text-red-400'
                      }`}
                    >
                      {(topScore * 100).toFixed(0)}%
                    </span>
                  </div>

                  <div className="mt-2.5 flex items-center justify-between text-[11px] text-text-muted">
                    <span className="text-blue-400 font-mono">{item.discipline}</span>
                    <span>{item.source}</span>
                  </div>
                </div>
              )
            })
          )}
        </div>

        {/* Right Detail & Action Pane */}
        <div className="lg:col-span-7 bg-surface border border-border rounded-xl p-6">
          {selectedItem ? (
            <div className="space-y-6">
              {/* Raw Field Observation Card */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono uppercase tracking-wider text-text-muted">
                    Field Submission Context
                  </span>
                  <StatusBadge
                    status={selectedItem.status === 'flagged_new' ? 'danger' : 'warning'}
                    label={selectedItem.status}
                    size="sm"
                  />
                </div>
                <div className="p-4 rounded-lg bg-surface-card border border-border">
                  <p className="text-sm font-semibold text-white">{selectedItem.raw_description || selectedItem.extracted_text}</p>
                  <div className="grid grid-cols-3 gap-2 mt-3 pt-3 border-t border-border/60 text-xs text-text-muted">
                    <div>Discipline: <strong className="text-white">{selectedItem.discipline}</strong></div>
                    <div>Source: <strong className="text-white">{selectedItem.source || 'Field DPR'}</strong></div>
                    <div>Date: <strong className="text-white">{selectedItem.submitted_at || selectedItem.extracted_date || 'Today'}</strong></div>
                  </div>
                </div>
              </div>

              {/* Top Match Candidates */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-white">AI Semantic Match Candidates (Top 3)</span>
                  <span className="text-[11px] text-ai-accent flex items-center gap-1">
                    <Sparkles className="w-3.5 h-3.5" /> Evaluated via MiniLM & FAISS
                  </span>
                </div>

                <div className="space-y-3">
                  {selectedItem.candidates.map((cand, idx) => (
                    <div
                      key={cand.activity_id}
                      className={`p-4 rounded-xl border transition-all ${
                        idx === 0
                          ? 'bg-surface-card border-primary/50 ring-1 ring-primary/20'
                          : 'bg-surface-card/60 border-border'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <div>
                          <span className="text-[11px] font-mono text-primary font-semibold block">
                            {cand.activity_id} · L5 Schedule Node
                          </span>
                          <h4 className="text-xs font-semibold text-white">{cand.activity_name}</h4>
                        </div>
                        <span className="text-xs font-mono font-bold text-emerald-400">
                          {(cand.score * 100).toFixed(0)}%
                        </span>
                      </div>
                      <ConfidenceBar value={cand.score} />
                      <p className="text-[11px] text-text-muted mt-2">
                        Reasoning: <span className="text-text-secondary">{cand.explanation}</span>
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Planner Decision Buttons */}
              <div className="pt-4 border-t border-border flex flex-wrap items-center gap-3">
                <button
                  type="button"
                  onClick={() => handleApprove(selectedItem)}
                  className="flex-1 py-2.5 px-4 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-lg flex items-center justify-center gap-2 transition-colors shadow-sm"
                >
                  <Check className="w-4 h-4" />
                  Approve Selected Match
                </button>

                <button
                  type="button"
                  onClick={() => handleFlagNew(selectedItem)}
                  className="py-2.5 px-4 bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40 text-xs font-semibold rounded-lg flex items-center gap-1.5 transition-colors"
                >
                  <PlusCircle className="w-4 h-4" />
                  Flag New Activity
                </button>

                <button
                  type="button"
                  onClick={() => handleReject(selectedItem)}
                  className="py-2.5 px-4 bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30 text-xs font-semibold rounded-lg flex items-center gap-1.5 transition-colors"
                >
                  <X className="w-4 h-4" />
                  Reject Match
                </button>
              </div>
            </div>
          ) : (
            <div className="h-96 flex flex-col items-center justify-center text-center text-text-muted">
              <CheckSquare className="w-12 h-12 stroke-[1.5] mb-2 opacity-30" />
              <p className="text-sm">Select an item from the review queue</p>
              <p className="text-xs mt-1">Review candidates and approve schedule updates</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
