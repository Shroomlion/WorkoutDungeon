import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Forward API calls to Django so the browser sees a single origin.
    // The React app fetches "/api/..." (relative URL) and never knows
    // Django lives on another port — which means session cookies and
    // CSRF behave exactly as they would in production behind one domain.
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
