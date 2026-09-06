import type { Metadata, Viewport } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'
import { Toaster } from 'react-hot-toast'
import { QueryProvider } from '@/components/providers/query-provider'
import './globals.css'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-jetbrains-mono',
  display: 'swap',
})

export const metadata: Metadata = {
  title: {
    default: 'NEXUS PM — AI-Powered Project Intelligence',
    template: '%s | NEXUS PM',
  },
  description: 'AI-driven project management platform for engineering & construction projects. Real-time schedule tracking, AI forecasting, and institutional memory.',
  keywords: ['project management', 'AI', 'schedule', 'EPC', 'construction', 'analytics'],
  authors: [{ name: 'NEXUS PM Team' }],
  manifest: '/manifest.json',
  icons: {
    icon: '/favicon.ico',
    apple: '/apple-touch-icon.png',
  },
  openGraph: {
    type: 'website',
    title: 'NEXUS PM — AI-Powered Project Intelligence',
    description: 'AI-driven project management platform for engineering & construction projects.',
    siteName: 'NEXUS PM',
  },
}

export const viewport: Viewport = {
  themeColor: '#0A0F1C',
  colorScheme: 'dark',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable} dark`} suppressHydrationWarning>
      <body className="bg-background text-neutral-100 font-sans antialiased min-h-screen">
        <QueryProvider>
          {children}
          <Toaster
            position="top-right"
            gutter={8}
            toastOptions={{
              duration: 4000,
              style: {
                background: '#111827',
                color: '#F9FAFB',
                border: '1px solid #1F2937',
                borderRadius: '10px',
                fontSize: '14px',
                fontFamily: 'var(--font-inter)',
              },
              success: {
                iconTheme: { primary: '#10B981', secondary: '#111827' },
                style: { borderLeft: '4px solid #10B981' },
              },
              error: {
                iconTheme: { primary: '#EF4444', secondary: '#111827' },
                style: { borderLeft: '4px solid #EF4444' },
              },
            }}
          />
        </QueryProvider>
      </body>
    </html>
  )
}
