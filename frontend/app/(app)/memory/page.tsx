'use client'

import { useState } from 'react'
import {
  MessageSquare, Send, Sparkles, BookOpen, Clock,
  ArrowRight, CheckCircle2, History, Database
} from 'lucide-react'
import toast from 'react-hot-toast'
import { aiApi, MemoryResponse } from '@/lib/api'
import { mockMemoryAnswer } from '@/lib/mock-data'

interface Message {
  role: 'user' | 'assistant'
  content: string
  sources?: MemoryResponse['sources']
  confidence?: number
}

const SAMPLE_QUERIES = [
  'What is the typical erection duration for 12-inch CS piping spool in monsoon?',
  'How often do field weld repairs occur in cross-country pipeline river crossings?',
  'What was the average productivity ratio for Civil excavation in Kaziranga terrain?',
  'What mitigation strategies were used when anchor block concrete failed 7-day cube tests?',
]

export default function MemoryPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content:
        'Greetings. I am the NEXUS Institutional Memory Copilot. I have indexed historical execution actuals, daily shift diaries, and lessons learned across past Oil India and PSU infrastructure projects. How can I assist your planning today?',
    },
  ])
  const [inputQuery, setInputQuery] = useState('')
  const [isSearching, setIsSearching] = useState(false)

  const handleSend = async (queryText?: string) => {
    const q = queryText || inputQuery
    if (!q.trim() || isSearching) return

    const userMsg: Message = { role: 'user', content: q }
    setMessages((prev) => [...prev, userMsg])
    setInputQuery('')
    setIsSearching(true)

    try {
      let res: MemoryResponse
      try {
        res = await aiApi.queryMemory(q)
      } catch {
        res = mockMemoryAnswer
      }

      setTimeout(() => {
        const assistantMsg: Message = {
          role: 'assistant',
          content: res.answer,
          sources: res.sources,
          confidence: res.confidence,
        }
        setMessages((prev) => [...prev, assistantMsg])
        setIsSearching(false)
      }, 1000)
    } catch {
      setIsSearching(false)
      toast.error('Failed to query institutional memory')
    }
  }

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-surface border border-border rounded-xl p-5">
        <div>
          <div className="flex items-center gap-2">
            <Database className="w-5 h-5 text-ai-accent" />
            <h1 className="text-xl font-bold text-white">Institutional Memory Copilot</h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-ai-accent/20 text-ai-accent font-mono border border-ai-accent/30">
              RAG · CHROMADB + GEMINI
            </span>
          </div>
          <p className="text-sm text-text-muted mt-1">
            Query empirical project actuals, historical bottlenecks, and discipline productivity ratios across past project closures
          </p>
        </div>

        <div className="flex items-center gap-2 bg-surface-card px-3 py-1.5 rounded-lg border border-border text-xs text-text-muted">
          <BookOpen className="w-4 h-4 text-primary" />
          <span>Corpus: <strong className="text-white">10 Seeded PSU Projects</strong></span>
        </div>
      </div>

      {/* Suggested Quick Queries */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1">
        <span className="text-xs text-text-muted shrink-0 flex items-center gap-1 font-medium">
          <Sparkles className="w-3.5 h-3.5 text-ai-accent" /> Benchmark Prompts:
        </span>
        {SAMPLE_QUERIES.map((sample, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => handleSend(sample)}
            className="text-xs whitespace-nowrap bg-surface hover:bg-surface-card border border-border text-text-secondary hover:text-white px-3 py-1.5 rounded-lg transition-colors shrink-0"
          >
            {sample}
          </button>
        ))}
      </div>

      {/* Chat Thread */}
      <div className="bg-surface border border-border rounded-xl p-6 min-h-[480px] flex flex-col justify-between space-y-4">
        <div className="space-y-4 overflow-y-auto max-h-[500px] pr-2">
          {messages.map((m, idx) => (
            <div
              key={idx}
              className={`flex flex-col ${m.role === 'user' ? 'items-end' : 'items-start'}`}
            >
              <div
                className={`max-w-2xl rounded-xl p-4 text-xs leading-relaxed ${
                  m.role === 'user'
                    ? 'bg-primary text-white font-medium'
                    : 'bg-surface-card border border-border text-text-secondary'
                }`}
              >
                <div className="flex items-center gap-2 mb-1 text-[11px] font-semibold text-text-muted">
                  {m.role === 'user' ? 'Planner Query' : 'NEXUS Institutional Memory'}
                  {m.confidence && (
                    <span className="text-emerald-400 font-mono">
                      · {(m.confidence * 100).toFixed(0)}% Citation Relevance
                    </span>
                  )}
                </div>
                <p className="whitespace-pre-line">{m.content}</p>

                {/* Sources Citation Cards */}
                {m.sources && m.sources.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-border/60 space-y-2">
                    <span className="text-[10px] font-mono text-ai-accent uppercase tracking-wider block">
                      Retrieved Past Project Evidences:
                    </span>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {m.sources.map((src) => (
                        <div
                          key={src.id}
                          className="p-2.5 rounded-lg bg-surface border border-border/80 text-[11px] space-y-1"
                        >
                          <div className="flex items-center justify-between text-[10px] text-text-muted">
                            <strong className="text-blue-400">{src.project_name}</strong>
                            <span className="font-mono">{src.date}</span>
                          </div>
                          <div className="font-medium text-white">{src.activity_name}</div>
                          <p className="text-text-muted italic line-clamp-2">&quot;{src.excerpt}&quot;</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}

          {isSearching && (
            <div className="flex items-center gap-2 text-xs text-ai-accent font-medium p-3 bg-surface-card rounded-xl border border-ai-accent/20 w-fit animate-pulse">
              <Sparkles className="w-4 h-4 animate-spin" /> Querying ChromaDB vector space and synthesizing institutional actuals...
            </div>
          )}
        </div>

        {/* Query Input Box */}
        <div className="pt-3 border-t border-border flex gap-2">
          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask anything regarding past actual durations, productivity norms, or delay causes..."
            className="flex-1 bg-surface-card border border-border rounded-xl px-4 py-3 text-xs text-white placeholder:text-text-muted focus:outline-none focus:border-ai-accent transition-colors"
          />
          <button
            type="button"
            onClick={() => handleSend()}
            disabled={!inputQuery.trim() || isSearching}
            className="px-5 py-3 bg-ai-accent hover:opacity-90 disabled:opacity-50 text-white text-xs font-semibold rounded-xl flex items-center gap-2 transition-all shrink-0"
          >
            <Send className="w-4 h-4" />
            Query Memory
          </button>
        </div>
      </div>
    </div>
  )
}
