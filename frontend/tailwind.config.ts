import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: 'class',
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#0A0F1C',
        surface: '#111827',
        'surface-2': '#161F2E',
        'surface-card': '#161F2E',
        'surface-elevated': '#1F2937',
        border: '#1F2937',
        'border-subtle': '#374151',
        'border-active': '#3B82F6',
        'text-primary': '#F9FAFB',
        'text-secondary': '#9CA3AF',
        'text-muted': '#6B7280',
        'ai-accent': '#8B5CF6',
        primary: {
          DEFAULT: '#3B82F6',
          hover: '#2563EB',
          50: '#EFF6FF', 100: '#DBEAFE', 200: '#BFDBFE', 300: '#93C5FD',
          400: '#60A5FA', 500: '#3B82F6', 600: '#2563EB', 700: '#1D4ED8',
          800: '#1E40AF', 900: '#1E3A8A',
        },
        success: {
          DEFAULT: '#10B981', 50: '#ECFDF5', 100: '#D1FAE5',
          500: '#10B981', 600: '#059669', 700: '#047857',
        },
        warning: {
          DEFAULT: '#F59E0B', 50: '#FFFBEB', 100: '#FEF3C7',
          500: '#F59E0B', 600: '#D97706', 700: '#B45309',
        },
        danger: {
          DEFAULT: '#EF4444', 50: '#FEF2F2', 100: '#FEE2E2',
          500: '#EF4444', 600: '#DC2626', 700: '#B91C1C',
        },
        ai: {
          DEFAULT: '#8B5CF6', 50: '#F5F3FF', 100: '#EDE9FE',
          400: '#A78BFA', 500: '#8B5CF6', 600: '#7C3AED', 700: '#6D28D9',
        },
        neutral: {
          50: '#F9FAFB', 100: '#F3F4F6', 200: '#E5E7EB', 300: '#D1D5DB',
          400: '#9CA3AF', 500: '#6B7280', 600: '#4B5563', 700: '#374151',
          800: '#1F2937', 900: '#111827', 950: '#0A0F1C',
        },
      },
      fontFamily: {
        sans: ['var(--font-inter)', 'system-ui', 'sans-serif'],
        mono: ['var(--font-jetbrains-mono)', 'monospace'],
      },
      backgroundImage: {
        'gradient-dark': 'linear-gradient(135deg, #0A0F1C 0%, #111827 50%, #0D1526 100%)',
        'gradient-primary': 'linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%)',
        'gradient-ai': 'linear-gradient(135deg, #4C1D95 0%, #8B5CF6 100%)',
        'gradient-surface': 'linear-gradient(180deg, #111827 0%, #0D1526 100%)',
      },
      boxShadow: {
        'glow-primary': '0 0 20px rgba(59,130,246,0.3)',
        'glow-ai': '0 0 20px rgba(139,92,246,0.3)',
        'glow-success': '0 0 20px rgba(16,185,129,0.3)',
        'glow-danger': '0 0 20px rgba(239,68,68,0.3)',
        'card': '0 4px 6px -1px rgba(0,0,0,0.4), 0 2px 4px -2px rgba(0,0,0,0.4)',
        'card-hover': '0 10px 15px -3px rgba(0,0,0,0.5), 0 4px 6px -4px rgba(0,0,0,0.5)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4,0,0.6,1) infinite',
        'float': 'float 6s ease-in-out infinite',
        'slide-up': 'slideUp 0.3s ease-out',
        'fade-in': 'fadeIn 0.4s ease-out',
        'wave': 'wave 1.5s ease-in-out infinite',
        'ping-slow': 'ping 2s cubic-bezier(0,0,0.2,1) infinite',
      },
      keyframes: {
        float: { '0%,100%': { transform: 'translateY(0)' }, '50%': { transform: 'translateY(-20px)' } },
        slideUp: { '0%': { transform: 'translateY(10px)', opacity: '0' }, '100%': { transform: 'translateY(0)', opacity: '1' } },
        fadeIn: { '0%': { opacity: '0' }, '100%': { opacity: '1' } },
        wave: { '0%,100%': { transform: 'scaleY(0.5)' }, '50%': { transform: 'scaleY(1.5)' } },
      },
    },
  },
  plugins: [],
}

export default config
