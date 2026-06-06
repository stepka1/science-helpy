/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#111111',
        paper: '#f5f3ef',
        line: '#d6d1c7',
        fog: '#ebe7de',
        muted: '#6c665f',
      },
      fontFamily: {
        sans: ['"Open Sans"', 'Arial', 'sans-serif'],
        mono: ['"IBM Plex Mono"', '"SFMono-Regular"', 'ui-monospace', 'monospace'],
      },
      boxShadow: {
        panel: '0 20px 60px rgba(17, 17, 17, 0.08)',
      },
    },
  },
  plugins: [],
}
