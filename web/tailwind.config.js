/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
    "./providers/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        surface: {
          DEFAULT: "#0c1222",
          raised: "#111827",
          overlay: "#161f33",
          border: "#243049",
        },
        brand: {
          DEFAULT: "#14b8a6",
          dim: "#0d9488",
          glow: "#2dd4bf",
          muted: "#134e4a",
        },
      },
      fontFamily: {
        sans: [
          "Inter",
          "Segoe UI",
          "system-ui",
          "-apple-system",
          "BlinkMacSystemFont",
          "Helvetica Neue",
          "Arial",
          "sans-serif",
        ],
        display: [
          "Inter",
          "Segoe UI",
          "system-ui",
          "-apple-system",
          "BlinkMacSystemFont",
          "Helvetica Neue",
          "Arial",
          "sans-serif",
        ],
        mono: ["Cascadia Code", "Consolas", "ui-monospace", "monospace"],
      },
      boxShadow: {
        card: "0 0 0 1px rgba(255,255,255,0.04), 0 8px 32px rgba(0,0,0,0.35)",
        "card-light": "0 1px 3px rgba(15,23,42,0.06), 0 8px 24px rgba(15,23,42,0.04)",
        glow: "0 0 40px rgba(20,184,166,0.12)",
        "glow-lg": "0 0 60px rgba(20,184,166,0.18)",
        "inner-glow": "inset 0 1px 0 0 rgba(255,255,255,0.06)",
      },
      borderRadius: {
        xl: "var(--radius)",
        "2xl": "calc(var(--radius) + 4px)",
        "3xl": "calc(var(--radius) + 8px)",
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        shimmer: "shimmer 2s linear infinite",
        "fade-up": "fade-up 0.5s ease-out forwards",
      },
      keyframes: {
        shimmer: {
          "0%": { backgroundPosition: "200% 0" },
          "100%": { backgroundPosition: "-200% 0" },
        },
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      backgroundImage: {
        "grid-pattern":
          "linear-gradient(to right, rgba(148,163,184,0.06) 1px, transparent 1px), linear-gradient(to bottom, rgba(148,163,184,0.06) 1px, transparent 1px)",
        shimmer:
          "linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.08) 50%, rgba(255,255,255,0) 100%)",
      },
      backgroundSize: {
        grid: "48px 48px",
      },
    },
  },
  plugins: [],
};
