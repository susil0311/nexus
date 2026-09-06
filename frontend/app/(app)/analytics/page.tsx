'use client'

import { useState } from 'react'
import {
  Brain, AlertTriangle, TrendingDown, Clock, ShieldAlert,
  Sliders, ArrowRight, CheckCircle2, ChevronRight
} from 'lucide-react'
import { mockForecast } from '@/lib/mock-data'
import { ForecastData } from '@/lib/api'
import { StatsCard } from '@/components/ui/stats-card'
import { ConfidenceBar } from '@/components/ui/confidence-bar'

export default function AnalyticsPage() {
  const [forecast] = useState<ForecastData>(mockForecast)
  const [productivitySlider, setProductivitySlider] = useState<number>(0)

  // Recalculate forecast dynamically with what-if slider
  const simulatedDelay = Math.max(0, forecast.delay_days - Math.round(productivitySlider * 0.4))

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-surface border border-border rounded-xl p-5">
        <div>
          <div className="flex items-center gap-2">
            <Brain className="w-5 h-5 text-ai-accent" />
            <h1 className="text-xl font-bold text-white">Delay Oracle — Predictive Intelligence</h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-ai-accent/20 text-ai-accent font-mono border border-ai-accent/30">
              XGBOOST ML PREDICTION ENGINE
            </span>
          </div>
          <p className="text-sm text-text-muted mt-1">
            2-4 week early warning on critical path completion slippage and root-cause risk decomposition
          </p>
        </div>

        <div className="flex items-center gap-2 bg-surface-card px-3.5 py-2 rounded-lg border border-border">
          <span className="text-xs text-text-muted">Forecast Confidence:</span>
          <span className="text-xs font-mono font-bold text-emerald-400">
            {(forecast.confidence * 100).toFixed(0)}% HIGH
          </span>
        </div>
      </div>

      {/* Hero Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="Predicted Finish Date"
          value={forecast.predicted_finish}
          subtitle={`Baseline: ${forecast.planned_finish}`}
          icon={Clock}
          variant="danger"
        />

        <StatsCard
          title="Estimated Slippage"
          value={`+${simulatedDelay} Days`}
          subtitle={productivitySlider > 0 ? `Reduced by ${forecast.delay_days - simulatedDelay}d via simulation` : 'Critical path overrun'}
          icon={TrendingDown}
          variant="danger"
        />

        <StatsCard
          title="Primary Risk Sector"
          value="Piping Erection"
          subtitle="23% lower velocity vs historical"
          icon={AlertTriangle}
          variant="warning"
        />

        <StatsCard
          title="Monsoon Weather Risk"
          value="Medium (38%)"
          subtitle="Buffer recommendation: 4 days"
          icon={ShieldAlert}
          variant="primary"
        />
      </div>

      {/* S-Curve Fan Chart & What-If Simulation */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* S-Curve Fan Visualizer */}
        <div className="lg:col-span-8 bg-surface border border-border rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-white">S-Curve Predictive Fan Envelope</h3>
              <p className="text-xs text-text-muted">Optimistic vs pessimistic completion probability cone</p>
            </div>
            <div className="flex items-center gap-3 text-xs">
              <span className="flex items-center gap-1 text-emerald-400">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" /> Optimistic
              </span>
              <span className="flex items-center gap-1 text-red-400">
                <span className="w-2.5 h-2.5 rounded-full bg-red-400" /> Pessimistic
              </span>
            </div>
          </div>

          <div className="h-60 flex flex-col justify-end gap-3 pt-6">
            <div className="grid grid-cols-5 gap-4 h-44 items-end border-b border-border/80 pb-2">
              {forecast.scurve_forecast.map((pt, idx) => (
                <div key={idx} className="flex flex-col items-center gap-1.5 h-full justify-end group">
                  <div className="w-full flex items-end justify-center gap-1 h-full">
                    {/* Planned */}
                    <div
                      style={{ height: `${pt.planned}%` }}
                      className="w-3 bg-blue-500/30 border-t-2 border-blue-400 rounded-t"
                      title={`Planned: ${pt.planned}%`}
                    />
                    {/* Optimistic */}
                    <div
                      style={{ height: `${pt.optimistic}%` }}
                      className="w-3 bg-emerald-500/50 border-t-2 border-emerald-400 rounded-t"
                      title={`Optimistic: ${pt.optimistic}%`}
                    />
                    {/* Pessimistic */}
                    <div
                      style={{ height: `${pt.pessimistic}%` }}
                      className="w-3 bg-red-500/50 border-t-2 border-red-400 rounded-t"
                      title={`Pessimistic: ${pt.pessimistic}%`}
                    />
                  </div>
                  <span className="text-[11px] font-mono text-text-muted">{pt.date}</span>
                </div>
              ))}
            </div>
            <div className="flex justify-between items-center text-xs text-text-muted">
              <span>Model: <strong className="text-white font-mono">Gradient Boosted Regressor</strong></span>
              <span className="text-amber-400">Variance: ±5.2 Days (95% CI)</span>
            </div>
          </div>

          {/* AI Narrative Box */}
          <div className="p-4 rounded-lg bg-surface-card border border-ai-accent/30 space-y-1.5">
            <div className="flex items-center gap-2 text-xs font-semibold text-ai-accent">
              <Brain className="w-3.5 h-3.5" /> Delay Oracle Executive Summary
            </div>
            <p className="text-xs text-text-secondary leading-relaxed">
              Based on the current SPI of <strong className="text-white">0.87</strong> and field weld failure repair frequency of <strong className="text-amber-400">8.3%</strong> in reach 3A, the model forecasts a <strong className="text-red-400">+{forecast.delay_days} day</strong> critical-path slippage. Primary recommendation: Mobilize additional AWS-certified welders to section CH 0+200 to neutralize divergence before monsoon onset.
            </p>
          </div>
        </div>

        {/* What-If Simulator */}
        <div className="lg:col-span-4 bg-surface border border-border rounded-xl p-5 flex flex-col justify-between space-y-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Sliders className="w-4 h-4 text-primary" />
              <h3 className="text-sm font-semibold text-white">What-If Scenario Simulator</h3>
            </div>
            <p className="text-xs text-text-muted mb-4">
              Simulate recovery actions by tuning productivity & resource acceleration parameters
            </p>

            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-xs mb-1.5">
                  <span className="text-text-muted">Piping Erection Acceleration:</span>
                  <span className="font-mono text-primary font-bold">+{productivitySlider}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="40"
                  step="5"
                  value={productivitySlider}
                  onChange={(e) => setProductivitySlider(Number(e.target.value))}
                  className="w-full accent-primary cursor-pointer"
                />
              </div>

              <div className="p-3 bg-surface-card border border-border rounded-lg space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-text-muted">Original Overrun:</span>
                  <span className="font-mono text-red-400 font-bold">+{forecast.delay_days} days</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-text-muted">Simulated Overrun:</span>
                  <span className="font-mono text-emerald-400 font-bold">+{simulatedDelay} days</span>
                </div>
                <div className="flex justify-between pt-1 border-t border-border font-medium">
                  <span className="text-text-secondary">Schedule Saved:</span>
                  <span className="font-mono text-primary font-bold">
                    {forecast.delay_days - simulatedDelay} working days
                  </span>
                </div>
              </div>
            </div>
          </div>

          <button
            type="button"
            onClick={() => setProductivitySlider(0)}
            className="w-full py-2 bg-surface-card hover:bg-surface-elevated text-text-muted hover:text-white border border-border text-xs rounded-lg transition-colors"
          >
            Reset Simulator
          </button>
        </div>
      </div>

      {/* Root Cause Decomposition */}
      <div className="bg-surface border border-border rounded-xl p-5">
        <h3 className="text-sm font-semibold text-white mb-1">Decomposed Root Cause Drivers</h3>
        <p className="text-xs text-text-muted mb-4">Calculated Shapley impact values across historical variance factors</p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {forecast.risk_factors.map((rf, idx) => (
            <div key={idx} className="p-4 rounded-lg bg-surface-card border border-border space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="text-xs font-semibold text-white">{rf.name}</h4>
                <span className="text-xs font-mono font-bold text-red-400">+{rf.impact_percent}% impact</span>
              </div>
              <p className="text-[11px] text-text-muted leading-relaxed">{rf.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
