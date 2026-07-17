import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#f8fafc",
        surface: "#07050a",
        brand: "#820ad1",
      },
    },
  },
  plugins: [],
};

export default config;
