import path from "path";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    // tailwindcss() must come before react() so Tailwind processes CSS first
    tailwindcss(),
    react(),
  ],
  resolve: {
    alias: {
      // "@" maps to "src/" - required by shadcn/ui components which import from "@/lib/utils"
      "@": path.resolve(__dirname, "./src"),
    },
  },
});
