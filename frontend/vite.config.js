import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    // Dev-only proxy — production uses VITE_API_URL env var via api.js
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
})
