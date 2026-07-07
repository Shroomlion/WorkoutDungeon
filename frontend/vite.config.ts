import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Forward API calls to Django so the browser sees a single origin —
    // session cookies and CSRF behave as they will in production.
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
