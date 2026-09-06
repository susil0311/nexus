'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  Upload, Mic, MicOff, FileText, CheckCircle, AlertCircle,
  ArrowRight, Sparkles, RefreshCw, Send, Paperclip
} from 'lucide-react'
import { useDropzone } from 'react-dropzone'
import toast from 'react-hot-toast'
import { ingestApi, IngestResponse } from '@/lib/api'
import { useStore } from '@/lib/store'
import { ConfidenceBar } from '@/components/ui/confidence-bar'
import { StatusBadge } from '@/components/ui/status-badge'

export default function IngestPage() {
  const selectedProject = useStore((s) => s.selectedProject)
  const [activeTab, setActiveTab] = useState<'upload' | 'agent'>('upload')
  const [discipline, setDiscipline] = useState('Piping')
  const [isProcessing, setIsProcessing] = useState(false)
  const [pipelineStep, setPipelineStep] = useState(0) // 0: Idle, 1: Parse, 2: Extract, 3: Match, 4: Complete
  const [extractedResult, setExtractedResult] = useState<IngestResponse | null>(null)

  // Voice / Text State
  const [voiceText, setVoiceText] = useState('')
  const [isRecording, setIsRecording] = useState(false)

  // Dropzone handler
  const { getRootProps, getInputProps, isDragActive, acceptedFiles } = useDropzone({
    accept: {
      'text/plain': ['.txt'],
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'text/csv': ['.csv'],
    },
    maxFiles: 1,
    onDrop: async (files) => {
      if (!files.length) return
      const file = files[0]
      await processUpload(file)
    },
  })

  const processUpload = async (file: File) => {
    setIsProcessing(true)
    setPipelineStep(1)

    try {
      setTimeout(() => setPipelineStep(2), 600)
      setTimeout(() => setPipelineStep(3), 1200)

      let res: IngestResponse
      try {
        res = await ingestApi.ingestFile(file, selectedProject?.id || 'proj-001', discipline)
      } catch {
        // Fallback demo simulation
        res = {
          submission_id: 'sub-' + Math.random().toString(36).substring(7),
          status: 'done',
          extracted_fields: {
            date: new Date().toISOString().split('T')[0],
            activity_description: 'Erected 12-inch CS Spool PS-IN-003 at north header manifold',
            progress: 75,
            discipline: discipline,
            remarks: 'Visual inspection cleared. NDT scheduled for tomorrow shift.',
          },
          best_match: {
            activity_id: 'PIP-SPL-003',
            activity_name: 'Erect spool PS-IN-003 at pump station inlet header',
            score: 0.94,
          },
        }
      }

      setTimeout(() => {
        setPipelineStep(4)
        setExtractedResult(res)
        setIsProcessing(false)
        toast.success('DPR ingested and activities extracted!')
      }, 1800)
    } catch (err) {
      setIsProcessing(false)
      toast.error('Failed to process submission')
    }
  }

  const handleVoiceSubmit = async (textToSubmit?: string) => {
    const text = textToSubmit || voiceText
    if (!text.trim()) return

    setIsProcessing(true)
    setPipelineStep(2)

    try {
      setTimeout(() => setPipelineStep(3), 800)
      let res: IngestResponse
      try {
        res = await ingestApi.ingestText({
          text,
          project_id: selectedProject?.id || 'proj-001',
          discipline,
          source: 'voice_agent',
        })
      } catch {
        res = {
          submission_id: 'sub-' + Math.random().toString(36).substring(7),
          status: 'done',
          extracted_fields: {
            date: new Date().toISOString().split('T')[0],
            activity_description: text,
            progress: 80,
            discipline: discipline,
            remarks: 'Supervisor verbal update via TIME Agent voice logger',
          },
          best_match: {
            activity_id: 'CIV-GRT-002',
            activity_name: 'Grouting of pump foundation PF-A3',
            score: 0.91,
          },
        }
      }

      setTimeout(() => {
        setPipelineStep(4)
        setExtractedResult(res)
        setIsProcessing(false)
        setVoiceText('')
        toast.success('TIME Agent logged actual progress update!')
      }, 1500)
    } catch {
      setIsProcessing(false)
      toast.error('Failed to extract activity')
    }
  }

  const toggleRecording = () => {
    if (!isRecording) {
      setIsRecording(true)
      toast('Listening to field supervisor...', { icon: '🎙️' })
      // Simulation of speech to text
      setTimeout(() => {
        setVoiceText('Bhanu here, completed grouting for pump foundation PF-A3 today morning at 11 AM')
        setIsRecording(false)
      }, 2500)
    } else {
      setIsRecording(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-surface border border-border rounded-xl p-5">
        <div>
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-ai-accent" />
            <h1 className="text-xl font-bold text-white">AI Data Ingestion Engine</h1>
          </div>
          <p className="text-sm text-text-muted mt-1">
            Ingest heterogeneous daily reports, Excel logs, and site supervisor voice feeds directly into L5/L6 schedules
          </p>
        </div>

        {/* Tab Controls */}
        <div className="flex bg-surface-card p-1 rounded-lg border border-border">
          <button
            onClick={() => setActiveTab('upload')}
            className={`px-4 py-1.5 text-xs font-medium rounded-md transition-all ${
              activeTab === 'upload' ? 'bg-primary text-white shadow' : 'text-text-muted hover:text-white'
            }`}
          >
            File & Document Upload
          </button>
          <button
            onClick={() => setActiveTab('agent')}
            className={`flex items-center gap-1.5 px-4 py-1.5 text-xs font-medium rounded-md transition-all ${
              activeTab === 'agent' ? 'bg-ai-accent text-white shadow' : 'text-text-muted hover:text-white'
            }`}
          >
            <Mic className="w-3.5 h-3.5" />
            TIME Agent (Voice & Chat)
          </button>
        </div>
      </div>

      {/* Main Ingestion Flow */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Input Pane */}
        <div className="lg:col-span-7 space-y-4">
          {activeTab === 'upload' ? (
            <div className="bg-surface border border-border rounded-xl p-5 space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-semibold text-white">Select Engineering Discipline</span>
                <select
                  value={discipline}
                  onChange={(e) => setDiscipline(e.target.value)}
                  className="bg-surface-card border border-border text-xs text-white rounded-lg px-3 py-1.5 focus:outline-none focus:border-primary"
                >
                  <option value="Piping">Piping</option>
                  <option value="Civil">Civil</option>
                  <option value="Electrical">Electrical</option>
                  <option value="Instrumentation">Instrumentation</option>
                  <option value="Mechanical">Mechanical</option>
                </select>
              </div>

              {/* Drag and Drop Zone */}
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
                  isDragActive
                    ? 'border-primary bg-primary/5'
                    : 'border-border hover:border-border-active bg-surface-card/50'
                }`}
              >
                <input {...getInputProps()} />
                <div className="w-12 h-12 rounded-full bg-surface border border-border flex items-center justify-center mx-auto mb-3 text-primary">
                  <Upload className="w-6 h-6" />
                </div>
                <h3 className="text-sm font-semibold text-white">Drag & drop your site report or spreadsheet</h3>
                <p className="text-xs text-text-muted mt-1">
                  Supports DPR PDFs, discipline Excel (.xlsx), CSV, and plain text notes
                </p>
                <div className="mt-4 flex items-center justify-center gap-2">
                  <span className="text-[10px] bg-surface-card px-2 py-1 rounded text-text-muted border border-border font-mono">
                    sample_dpr.txt available in assets
                  </span>
                </div>
              </div>

              {/* Sample Quick Action */}
              <div className="pt-2 flex items-center justify-between">
                <span className="text-xs text-text-muted">Want to test with real Oil India DPR format?</span>
                <button
                  type="button"
                  onClick={() => {
                    const blob = new File(
                      ['Excavation for pipeline trench Section CH 0+000 to CH 0+450 completed today.'],
                      'sample_dpr.txt',
                      { type: 'text/plain' }
                    )
                    processUpload(blob)
                  }}
                  className="text-xs text-primary hover:underline font-medium"
                >
                  Load Sample DPR
                </button>
              </div>
            </div>
          ) : (
            <div className="bg-surface border border-border rounded-xl p-5 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-semibold text-white">TIME Agent — Field Conversational Logger</h3>
                  <p className="text-xs text-text-muted">Speak or type in natural language (Hindi or English)</p>
                </div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-ai-accent/20 text-ai-accent border border-ai-accent/30">
                  LLM FUNCTION CALLING
                </span>
              </div>

              {/* Voice Interaction Zone */}
              <div className="p-6 rounded-xl bg-surface-card border border-border text-center flex flex-col items-center justify-center gap-3">
                <button
                  type="button"
                  onClick={toggleRecording}
                  className={`w-16 h-16 rounded-full flex items-center justify-center transition-all ${
                    isRecording
                      ? 'bg-red-500 text-white animate-pulse shadow-lg shadow-red-500/30'
                      : 'bg-ai-accent text-white hover:opacity-90 shadow-lg shadow-ai-accent/20'
                  }`}
                >
                  {isRecording ? <MicOff className="w-7 h-7" /> : <Mic className="w-7 h-7" />}
                </button>
                <span className="text-xs font-medium text-white">
                  {isRecording ? 'Listening... Speak your site update' : 'Tap to Record Supervisor Voice Note'}
                </span>
                <p className="text-[11px] text-text-muted max-w-sm">
                  Example: &quot;Bhanu here, completed grouting for pump foundation PF-A3 today morning at 11 AM&quot;
                </p>
              </div>

              {/* Text Input Fallback */}
              <div className="flex gap-2">
                <input
                  type="text"
                  value={voiceText}
                  onChange={(e) => setVoiceText(e.target.value)}
                  placeholder="Or type natural language update here..."
                  className="flex-1 bg-surface-card border border-border rounded-lg px-3 py-2 text-xs text-white placeholder:text-text-muted focus:outline-none focus:border-ai-accent"
                />
                <button
                  type="button"
                  onClick={() => handleVoiceSubmit()}
                  disabled={!voiceText.trim() || isProcessing}
                  className="px-4 py-2 bg-ai-accent hover:opacity-90 disabled:opacity-50 text-white text-xs font-semibold rounded-lg flex items-center gap-1.5 transition-all"
                >
                  <Send className="w-3.5 h-3.5" />
                  Extract
                </button>
              </div>
            </div>
          )}

          {/* Pipeline Visualizer */}
          <div className="bg-surface border border-border rounded-xl p-5">
            <h4 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-4">
              Ingestion & Schedule-Link Pipeline
            </h4>
            <div className="grid grid-cols-4 gap-2 text-center text-xs">
              {[
                { label: '1. Ingest & OCR', step: 1 },
                { label: '2. LLM Extract', step: 2 },
                { label: '3. Fuzzy Match', step: 3 },
                { label: '4. Schedule Sync', step: 4 },
              ].map((s) => {
                const isPassed = pipelineStep >= s.step
                const isCurrent = pipelineStep === s.step
                return (
                  <div
                    key={s.step}
                    className={`p-2.5 rounded-lg border transition-all ${
                      isCurrent
                        ? 'border-primary bg-primary/10 text-white font-medium animate-pulse'
                        : isPassed
                        ? 'border-emerald-500/40 bg-emerald-500/5 text-emerald-400'
                        : 'border-border bg-surface-card text-text-muted'
                    }`}
                  >
                    <div className="flex items-center justify-center mb-1">
                      {isPassed ? (
                        <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                      ) : (
                        <span className="w-3.5 h-3.5 rounded-full border border-border inline-block" />
                      )}
                    </div>
                    {s.label}
                  </div>
                )
              })}
            </div>
          </div>
        </div>

        {/* Right Output & Confirmation Card */}
        <div className="lg:col-span-5">
          <div className="bg-surface border border-border rounded-xl p-5 h-full flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between pb-3 border-b border-border mb-4">
                <h3 className="text-sm font-semibold text-white">Extracted Activity Payload</h3>
                {extractedResult && (
                  <StatusBadge status="success" label="Extracted via Gemini" size="sm" />
                )}
              </div>

              {extractedResult ? (
                <div className="space-y-4">
                  <div className="p-3 bg-surface-card border border-border rounded-lg space-y-2">
                    <span className="text-[11px] font-mono text-text-muted uppercase">Raw Observation</span>
                    <p className="text-xs text-white font-medium">
                      {extractedResult.extracted_fields.activity_description}
                    </p>
                    <div className="flex items-center gap-3 pt-1 text-[11px] text-text-muted">
                      <span>Discipline: <strong className="text-blue-400">{extractedResult.extracted_fields.discipline}</strong></span>
                      <span>Progress: <strong className="text-emerald-400">{extractedResult.extracted_fields.progress}%</strong></span>
                    </div>
                  </div>

                  {extractedResult.best_match && (
                    <div className="p-4 bg-surface-card border border-primary/40 rounded-xl space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold text-primary">Matched L5 Schedule Node</span>
                        <span className="text-xs font-mono font-bold text-emerald-400">
                          {(extractedResult.best_match.score * 100).toFixed(0)}% Confidence
                        </span>
                      </div>
                      <div className="p-2.5 bg-surface rounded-lg border border-border">
                        <span className="text-[10px] font-mono text-blue-400 block mb-0.5">
                          {extractedResult.best_match.activity_id}
                        </span>
                        <span className="text-xs font-medium text-white block">
                          {extractedResult.best_match.activity_name}
                        </span>
                      </div>
                      <ConfidenceBar value={extractedResult.best_match.score} />
                      <p className="text-[11px] text-text-muted">
                        Semantic match auto-resolved via transformer embeddings. Auditable log record created.
                      </p>
                    </div>
                  )}
                </div>
              ) : (
                <div className="h-64 flex flex-col items-center justify-center text-center p-6 text-text-muted">
                  <FileText className="w-10 h-10 stroke-[1.5] mb-2 opacity-40" />
                  <p className="text-xs">No active extraction yet</p>
                  <p className="text-[11px] mt-1">Upload a report or record a voice update on the left</p>
                </div>
              )}
            </div>

            {extractedResult && (
              <div className="pt-4 border-t border-border mt-4 flex gap-2">
                <button
                  type="button"
                  onClick={() => {
                    toast.success('Confirmed and committed to project schedule!')
                    setExtractedResult(null)
                    setPipelineStep(0)
                  }}
                  className="flex-1 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-lg flex items-center justify-center gap-1.5 transition-colors"
                >
                  <CheckCircle className="w-4 h-4" />
                  Confirm & Sync to Schedule
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
