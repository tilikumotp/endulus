/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["'IBM Plex Sans'", "system-ui", "-apple-system", "sans-serif"],
        mono: ["'IBM Plex Mono'", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      colors: {
        ink: {
          deep: "#07080d",
          bg: "#0b0d14",
          card: "#11141c",
          raised: "#1a1e28",
          primary: "#eef0f5",
          secondary: "#a3a9b8",
          muted: "#7a8296",
          accent: "#4c8bf5",
          ok: "#4cc38a",
          warn: "#e5484d",
        },
      },
      transitionTimingFunction: {
        instrument: "cubic-bezier(0.22, 1, 0.36, 1)",
      },
    },
  },
  plugins: [],
};
