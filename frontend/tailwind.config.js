/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: "#F6F4ED",
        surface: "#FFFDF8",
        ink: {
          DEFAULT: "#182724",
          light: "#2B3C38",
        },
        secondary: "#68746E",
        muted: "#87918B",
        border: "#E2E3DB",
        teal: {
          brand: "#17A982",
          mint: "#DDF4E9",
          dark: "#0F7A5E",
        },
        cobalt: {
          DEFAULT: "#536FF1",
          light: "#EAEFFF",
        },
        coral: {
          DEFAULT: "#ED8B76",
          light: "#FDF0ED",
        },
        gold: {
          DEFAULT: "#D5A747",
          light: "#FBF5E8",
        },
        violet: {
          DEFAULT: "#8676D8",
          light: "#F1EFFF",
        },
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'system-ui', 'sans-serif'],
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      boxShadow: {
        'paper': '0 1px 3px rgba(24, 39, 36, 0.04), 0 4px 12px rgba(24, 39, 36, 0.03)',
        'paper-hover': '0 4px 12px rgba(24, 39, 36, 0.08), 0 12px 28px rgba(24, 39, 36, 0.06)',
        'blueprint': '0 0 0 1px #E2E3DB, 0 4px 16px rgba(23, 169, 130, 0.06)',
      },
    },
  },
  plugins: [],
}
