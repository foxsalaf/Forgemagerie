import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        dofus: {
          gold: '#FFD700',
          brown: '#8B4513',
          blue: '#4169E1',
          green: '#32CD32',
          red: '#DC143C',
          purple: '#9932CC',
        }
      },
      fontFamily: {
        'dofus': ['Georgia', 'serif'],
      }
    },
  },
  plugins: [],
}
export default config