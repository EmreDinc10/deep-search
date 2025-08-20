import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Deep Search',
  description: 'Parallel search across multiple sources with AI synthesis',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50 min-h-screen">
        <div className="container mx-auto px-4 py-8">
          <header className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">Deep Search</h1>
            <p className="text-gray-600">Parallel search across multiple sources with AI synthesis</p>
          </header>
          {children}
        </div>
      </body>
    </html>
  )
}
