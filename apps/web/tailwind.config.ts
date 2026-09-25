import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#09090b", // zinc-950
        foreground: "#fafafa", // zinc-50
        muted: "#27272a", // zinc-800
        mutedForeground: "#a1a1aa", // zinc-400
        border: "#27272a", // zinc-800
        card: "#09090b", // zinc-950
        cardForeground: "#fafafa", // zinc-50
        primary: "#fafafa", // zinc-50
        primaryForeground: "#18181b", // zinc-900
        secondary: "#27272a", // zinc-800
        secondaryForeground: "#fafafa", // zinc-50
        accent: "#27272a", // zinc-800
        accentForeground: "#fafafa", // zinc-50
        destructive: "#ef4444", // red-500
        destructiveForeground: "#fafafa", // zinc-50
        ring: "#d4d4d8", // zinc-300
      },
    },
  },
  plugins: [],
};
export default config;
