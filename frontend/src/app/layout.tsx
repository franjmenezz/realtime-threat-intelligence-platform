import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Toaster } from 'react-hot-toast'

const inter = Inter({ subsets: ['latin'], variable: '--font-geist-sans' })

export const metadata: Metadata = {
  title: 'Threat Intelligence Pipeline',
  description: 'Real-time IoC ingestion, enrichment and risk scoring platform',
  icons: { icon: '/favicon.ico' },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans bg-background text-foreground`}>
        {children}
        <Toaster
          position="bottom-right"
          toastOptions={{
            style: {
              background: 'hsl(220, 14%, 10%)',
              color:      'hsl(210, 20%, 92%)',
              border:     '1px solid hsl(220, 13%, 18%)',
              fontFamily: 'var(--font-geist-sans)',
            },
          }}
        />
      </body>
    </html>
  )
}
