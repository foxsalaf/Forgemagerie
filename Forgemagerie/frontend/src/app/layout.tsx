import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Toaster } from 'react-hot-toast'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Forgemagerie - Analyse de Rentabilité Dofus',
  description: 'Application d\'analyse de rentabilité pour la forgemagie Dofus. Calculez les profits de vos forgemagie en temps réel.',
  keywords: 'dofus, forgemagie, joaillomage, rentabilité, hdv, analyse',
  authors: [{ name: 'Salaf' }],
  viewport: 'width=device-width, initial-scale=1',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="fr">
      <body className={inter.className}>
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
          <header className="bg-white shadow-sm border-b border-gray-200">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between items-center py-4">
                <div className="flex items-center space-x-4">
                  <h1 className="text-2xl font-bold text-gray-900 font-dofus">
                    🔨 Forgemagerie
                  </h1>
                  <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                    v1.0.0
                  </span>
                </div>
                <nav className="flex items-center space-x-6">
                  <a href="#" className="text-gray-600 hover:text-gray-900 transition-colors">
                    Analyse
                  </a>
                  <a href="#" className="text-gray-600 hover:text-gray-900 transition-colors">
                    Favoris
                  </a>
                  <a href="#" className="text-gray-600 hover:text-gray-900 transition-colors">
                    Guide
                  </a>
                </nav>
              </div>
            </div>
          </header>
          
          <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {children}
          </main>
          
          <footer className="bg-gray-50 border-t border-gray-200 mt-16">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
              <div className="text-center text-gray-600">
                <p>© 2024 Forgemagerie - Analyse de rentabilité pour joaillomages Dofus</p>
                <p className="text-sm mt-2">
                  Données fournies par DofAPI • Version {process.env.NODE_ENV}
                </p>
              </div>
            </div>
          </footer>
        </div>
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
          }}
        />
      </body>
    </html>
  )
}