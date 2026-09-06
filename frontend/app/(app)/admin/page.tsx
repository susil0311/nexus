'use client'

import { useState } from 'react'
import {
  Settings, Users, Shield, Database, Key,
  CheckCircle2, RefreshCw, Terminal, Sliders
} from 'lucide-react'
import toast from 'react-hot-toast'

export default function AdminPage() {
  const [modelProvider, setModelProvider] = useState('gemini-1.5-flash')
  const [mockAiMode, setMockAiMode] = useState(false)
  const [autoApproveThreshold, setAutoApproveThreshold] = useState(0.85)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-surface border border-border rounded-xl p-5">
        <div>
          <div className="flex items-center gap-2">
            <Settings className="w-5 h-5 text-text-secondary" />
            <h1 className="text-xl font-bold text-white">System Administration & Model Governance</h1>
          </div>
          <p className="text-sm text-text-muted mt-1">
            Configure LLM parameters, audit immutability logs, and manage project role-based access control
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* AI & Model Tuning */}
        <div className="bg-surface border border-border rounded-xl p-5 space-y-4">
          <div className="flex items-center gap-2 pb-2 border-b border-border">
            <Sliders className="w-4 h-4 text-ai-accent" />
            <h3 className="text-sm font-semibold text-white">AI Engine Configuration</h3>
          </div>

          <div className="space-y-3 text-xs">
            <div>
              <label className="text-text-muted block mb-1">Primary LLM Extractor</label>
              <select
                value={modelProvider}
                onChange={(e) => setModelProvider(e.target.value)}
                className="w-full bg-surface-card border border-border text-white rounded-lg p-2 focus:outline-none focus:border-ai-accent"
              >
                <option value="gemini-1.5-flash">Google Gemini 1.5 Flash (Recommended)</option>
                <option value="ollama-llama3">Ollama Local Llama 3 (Offline Edge)</option>
                <option value="gpt-4o-mini">OpenAI GPT-4o Mini (Fallback)</option>
              </select>
            </div>

            <div>
              <div className="flex justify-between mb-1">
                <span className="text-text-muted">Auto-Approve Match Threshold:</span>
                <span className="font-mono text-emerald-400 font-bold">
                  {(autoApproveThreshold * 100).toFixed(0)}%
                </span>
              </div>
              <input
                type="range"
                min="0.70"
                max="0.95"
                step="0.05"
                value={autoApproveThreshold}
                onChange={(e) => setAutoApproveThreshold(Number(e.target.value))}
                className="w-full accent-emerald-500 cursor-pointer"
              />
              <span className="text-[11px] text-text-muted">
                Matches with confidence above this threshold bypass planner review queue
              </span>
            </div>

            <div className="pt-2 flex items-center justify-between p-3 rounded-lg bg-surface-card border border-border">
              <div>
                <span className="font-medium text-white block">Offline Mock Data Mode</span>
                <span className="text-[11px] text-text-muted">
                  Use deterministic synthetic responses for demo reliability
                </span>
              </div>
              <button
                type="button"
                onClick={() => {
                  setMockAiMode(!mockAiMode)
                  toast.success(`Mock AI Mode ${!mockAiMode ? 'Activated' : 'Deactivated'}`)
                }}
                className={`w-11 h-6 rounded-full transition-colors relative ${
                  mockAiMode ? 'bg-primary' : 'bg-surface-elevated border border-border'
                }`}
              >
                <span
                  className={`w-4 h-4 rounded-full bg-white absolute top-1 transition-transform ${
                    mockAiMode ? 'left-6' : 'left-1'
                  }`}
                />
              </button>
            </div>
          </div>
        </div>

        {/* Audit Trail & Immutability */}
        <div className="bg-surface border border-border rounded-xl p-5 space-y-4">
          <div className="flex items-center gap-2 pb-2 border-b border-border">
            <Shield className="w-4 h-4 text-emerald-400" />
            <h3 className="text-sm font-semibold text-white">Cryptographic Audit Trail (SHA-256)</h3>
          </div>

          <div className="space-y-2.5 text-xs">
            {[
              {
                action: 'ACTUAL_PROGRESS_COMMITTED',
                entity: 'PIP-WLD-003',
                hash: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                time: '10 mins ago',
              },
              {
                action: 'MATCH_APPROVED_BY_PLANNER',
                entity: 'CIV-GRT-002',
                hash: '8f434346648f6b96df89dda901c5176b10a6d83961dd3c1ac88b59b2dc327aa4',
                time: '45 mins ago',
              },
              {
                action: 'SCHEDULE_IMPORT_XER',
                entity: 'KPE-2024 (245 nodes)',
                hash: 'ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb',
                time: '2 hours ago',
              },
            ].map((entry, idx) => (
              <div key={idx} className="p-3 bg-surface-card border border-border rounded-lg space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-primary text-[11px] font-semibold">{entry.action}</span>
                  <span className="text-[10px] text-text-muted">{entry.time}</span>
                </div>
                <div className="text-text-secondary text-[11px]">Node: {entry.entity}</div>
                <div className="text-[10px] font-mono text-text-muted truncate">
                  SHA: <span className="text-white">{entry.hash}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
