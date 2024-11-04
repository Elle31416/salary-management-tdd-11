/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['"DM Serif Display"', 'serif'],
        body: ['"DM Sans"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        ink: {
          950: '#0A0A0F',
          900: '#12121A',
          800: '#1C1C28',
          700: '#252535',
          600: '#32324A',
        },
        gold: {
          400: '#F4C842',
          500: '#E8B422',
          600: '#C49010',
        },
        teal: {
          400: '#2DD4BF',
          500: '#14B8A6',
          600: '#0D9488',
        }
      }
    }
  },
  plugins: []
}
