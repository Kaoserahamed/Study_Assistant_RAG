/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        paper: {
          DEFAULT: '#F6F4EF',
          dim: '#EFEBE1',
          line: '#DAD5C8',
        },
        ink: {
          DEFAULT: '#1E2235',
          soft: '#4A4E63',
          faint: '#8A8DA0',
        },
        highlighter: {
          DEFAULT: '#FFC857',
          soft: '#FFE1A3',
          dark: '#C99A2E',
        },
        denim: {
          DEFAULT: '#3D5A80',
          soft: '#6E8CAD',
          dark: '#2A4059',
        },
        mint: {
          DEFAULT: '#5FAE85',
          soft: '#CFE8DC',
          dark: '#3D7D5E',
        },
        rust: {
          DEFAULT: '#B8543D',
          soft: '#F1D9D2',
          dark: '#8F3E2B',
        },
      },
      fontFamily: {
        display: ['"Source Serif 4"', 'Georgia', 'serif'],
        body: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'monospace'],
      },
      boxShadow: {
        tab: '2px 2px 0 0 rgba(30, 34, 53, 0.08)',
        card: '0 1px 2px rgba(30,34,53,0.06), 0 1px 0 rgba(30,34,53,0.04)',
        popover: '0 12px 32px rgba(30,34,53,0.18)',
      },
      borderRadius: {
        card: '10px',
      },
      keyframes: {
        'fade-in': {
          '0%': { opacity: 0, transform: 'translateY(4px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
        'pulse-dot': {
          '0%, 80%, 100%': { transform: 'scale(0.6)', opacity: 0.4 },
          '40%': { transform: 'scale(1)', opacity: 1 },
        },
      },
      animation: {
        'fade-in': 'fade-in 0.25s ease-out',
        'pulse-dot': 'pulse-dot 1.2s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
