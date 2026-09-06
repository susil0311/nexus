'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { Eye, EyeOff, Zap, Brain, Shield, BarChart3, Loader2 } from 'lucide-react'
import { authApi } from '@/lib/api'
import { useStore } from '@/lib/store'
import { cn } from '@/lib/utils'

// ─── Floating Particle ────────────────────────────────────────────────────────
function Particle({ index }: { index: number }) {
  const size = Math.random() * 4 + 2
  const left = Math.random() * 100
  const duration = Math.random() * 20 + 15
  const delay = Math.random() * 10
  const opacity = Math.random() * 0.5 + 0.1

  return (
    <div
      className="absolute rounded-full pointer-events-none"
      style={{
        width: size,
        height: size,
        left: `${left}%`,
        bottom: '-10px',
        background: index % 3 === 0 ? '#3B82F6' : index % 3 === 1 ? '#8B5CF6' : '#10B981',
        opacity,
        animation: `particleFloat ${duration}s ${delay}s linear infinite`,
      }}
    />
  )
}

// ─── Feature Highlight ────────────────────────────────────────────────────────
function Feature({ icon, title, desc }: { icon: React.ReactNode; title: string; desc: string }) {
  return (
    <div className="flex items-start gap-3">
      <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-primary/20 border border-primary/30 flex items-center justify-center text-primary">
        {icon}
      </div>
      <div>
        <p className="text-sm font-semibold text-neutral-100">{title}</p>
        <p className="text-xs text-neutral-400 mt-0.5">{desc}</p>
      </div>
    </div>
  )
}

const DEMO_CREDENTIALS = [
  { email: 'pm@nexus.com', password: 'nexus123', role: 'Project Manager', color: 'primary' },
  { email: 'field@nexus.com', password: 'nexus123', role: 'Field Engineer', color: 'success' },
  { email: 'admin@nexus.com', password: 'nexus123', role: 'Administrator', color: 'ai' },
]

export default function LoginPage() {
  const router = useRouter()
  const setAuth = useStore((s) => s.setAuth)
  const isAuthenticated = useStore((s) => s.isAuthenticated)

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPass, setShowPass] = useState(false)
  const [loading, setLoading] = useState(false)
  const [particles] = useState(() => Array.from({ length: 30 }, (_, i) => i))

  useEffect(() => {
    if (isAuthenticated) router.replace('/dashboard')
  }, [isAuthenticated, router])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email || !password) {
      toast.error('Please enter email and password')
      return
    }
    setLoading(true)
    try {
      const res = await authApi.login(email, password)
      setAuth(res.user, res.access_token)
      toast.success(`Welcome back, ${res.user.full_name}!`)
      router.push('/dashboard')
    } catch {
      // Fallback: demo credentials
      const demo = DEMO_CREDENTIALS.find((d) => d.email === email && d.password === password)
      if (demo) {
        const mockUser = {
          id: 'u-mock',
          email: demo.email,
          full_name: demo.role,
          role: (demo.role === 'Administrator' ? 'admin' : demo.role === 'Project Manager' ? 'pm' : 'field') as 'admin' | 'pm' | 'field',
        }
        setAuth(mockUser, 'mock-token-' + Date.now())
        toast.success(`Welcome, ${mockUser.full_name}! (Demo Mode)`)
        router.push('/dashboard')
      } else {
        toast.error('Invalid credentials. Try the demo credentials below.')
      }
    } finally {
      setLoading(false)
    }
  }

  const fillDemo = (cred: typeof DEMO_CREDENTIALS[0]) => {
    setEmail(cred.email)
    setPassword(cred.password)
  }

  return (
    <div className="min-h-screen flex">
      {/* ── Left Panel ───────────────────────────────────────────────────────── */}
      <div className="hidden lg:flex lg:w-1/2 relative flex-col justify-between p-12 overflow-hidden"
        style={{ background: 'linear-gradient(135deg, #040810 0%, #0A0F1C 40%, #0D1A3A 100%)' }}>
        {/* Particles */}
        <div className="absolute inset-0 overflow-hidden">
          {particles.map((i) => <Particle key={i} index={i} />)}
        </div>

        {/* Glow orbs */}
        <div className="absolute top-20 left-20 w-64 h-64 rounded-full bg-primary/10 blur-3xl pointer-events-none" />
        <div className="absolute bottom-32 right-10 w-48 h-48 rounded-full bg-ai/10 blur-3xl pointer-events-none" />

        {/* Logo */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="relative z-10"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-primary flex items-center justify-center shadow-glow-primary">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white tracking-tight">NEXUS PM</h1>
              <p className="text-xs text-primary/70 font-medium tracking-widest uppercase">AI Project Intelligence</p>
            </div>
          </div>
        </motion.div>

        {/* Hero text */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="relative z-10 space-y-6"
        >
          <div>
            <h2 className="text-4xl font-bold text-white leading-tight mb-4">
              Your{' '}
              <span className="gradient-text">AI-powered</span>
              <br />
              command center
            </h2>
            <p className="text-neutral-400 text-base leading-relaxed max-w-sm">
              Real-time schedule intelligence, delay forecasting, and institutional memory
              for EPC and infrastructure projects.
            </p>
          </div>

          <div className="space-y-4">
            <Feature
              icon={<Brain className="w-5 h-5" />}
              title="Delay Oracle AI"
              desc="Predicts project overruns weeks before they happen using ML models trained on historical data"
            />
            <Feature
              icon={<BarChart3 className="w-5 h-5" />}
              title="Live S-Curve Analytics"
              desc="Real-time SPI/CPI tracking with automated field report ingestion via voice or document upload"
            />
            <Feature
              icon={<Shield className="w-5 h-5" />}
              title="Anomaly Sentinel"
              desc="Detects productivity drops, data gaps, and schedule deviations the moment they occur"
            />
          </div>
        </motion.div>

        {/* Bottom watermark */}
        <div className="relative z-10">
          <p className="text-neutral-600 text-xs">© 2026 NEXUS PM · Built for EPC Excellence</p>
        </div>
      </div>

      {/* ── Right Panel ──────────────────────────────────────────────────────── */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-background">
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-md space-y-8"
        >
          {/* Mobile logo */}
          <div className="lg:hidden flex items-center gap-3 mb-8">
            <div className="w-9 h-9 rounded-xl bg-gradient-primary flex items-center justify-center">
              <Zap className="w-4 h-4 text-white" />
            </div>
            <h1 className="text-xl font-bold gradient-text">NEXUS PM</h1>
          </div>

          <div>
            <h2 className="text-2xl font-bold text-neutral-100">Sign in to your workspace</h2>
            <p className="text-neutral-400 text-sm mt-1">Enter your credentials to access the project dashboard</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email */}
            <div className="space-y-1.5">
              <label htmlFor="email" className="text-sm font-medium text-neutral-300">
                Email address
              </label>
              <input
                id="email"
                type="email"
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input"
                placeholder="you@company.com"
                disabled={loading}
              />
            </div>

            {/* Password */}
            <div className="space-y-1.5">
              <label htmlFor="password" className="text-sm font-medium text-neutral-300">
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPass ? 'text' : 'password'}
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="input pr-10"
                  placeholder="••••••••"
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={() => setShowPass(!showPass)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-500 hover:text-neutral-300 transition-colors"
                >
                  {showPass ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Role preview */}
            {email && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="flex items-center gap-2 p-3 rounded-lg bg-surface-2 border border-border"
              >
                <div className={cn('w-2 h-2 rounded-full',
                  email.includes('admin') ? 'bg-ai' :
                  email.includes('pm') ? 'bg-primary' : 'bg-success'
                )} />
                <span className="text-xs text-neutral-400">Signing in as:</span>
                <span className={cn('text-xs font-semibold',
                  email.includes('admin') ? 'text-ai' :
                  email.includes('pm') ? 'text-primary' : 'text-success'
                )}>
                  {email.includes('admin') ? 'Administrator' : email.includes('pm') ? 'Project Manager' : 'Field Engineer'}
                </span>
              </motion.div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full py-3 text-base"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          {/* Demo credentials */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <div className="flex-1 h-px bg-border" />
              <span className="text-xs text-neutral-500 px-2">Demo Credentials</span>
              <div className="flex-1 h-px bg-border" />
            </div>
            <div className="grid gap-2">
              {DEMO_CREDENTIALS.map((cred) => (
                <button
                  key={cred.email}
                  type="button"
                  onClick={() => fillDemo(cred)}
                  className="flex items-center justify-between p-3 rounded-lg border border-border bg-surface hover:border-border-subtle hover:bg-surface-2 transition-all text-left group"
                >
                  <div>
                    <p className={cn('text-xs font-semibold',
                      cred.color === 'primary' ? 'text-primary' :
                      cred.color === 'success' ? 'text-success' : 'text-ai'
                    )}>{cred.role}</p>
                    <p className="text-xs text-neutral-500 font-mono mt-0.5">{cred.email}</p>
                  </div>
                  <span className="text-xs text-neutral-600 group-hover:text-neutral-400 transition-colors">
                    Click to fill →
                  </span>
                </button>
              ))}
            </div>
            <p className="text-xs text-center text-neutral-600">Password for all demo accounts: <code className="text-neutral-400 font-mono bg-surface px-1 py-0.5 rounded">nexus123</code></p>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
