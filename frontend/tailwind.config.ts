import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: {
          DEFAULT: "#12203A",
          light: "#1B2E52",
          dark: "#0B1526",
        },
        signal: {
          DEFAULT: "#F5A623",
          light: "#FFC15E",
          dark: "#C9820F",
        },
        surface: {
          DEFAULT: "#F5F7FA",
          dark: "#0B0F14",
        },
      },
      fontFamily: {
        display: ["var(--font-display)", "sans-serif"],
        sans: ["var(--font-body)", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
