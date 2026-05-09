/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        dark: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#1e293b',
          800: '#0f172a',
          900: '#0a0e1a',
          950: '#060810',
        },
        accent: {
          green: '#00c853',
          red: '#ff1744',
          blue: '#2979ff',
          yellow: '#ffd600',
          purple: '#7c4dff',
        },
      },
    },
  },
  plugins: [],
}
