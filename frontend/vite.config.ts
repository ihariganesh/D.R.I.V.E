import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      '/api': {
        target: process.env.REACT_APP_API_URL || 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: process.env.REACT_APP_WS_URL || 'ws://localhost:8000',
        ws: true,
      },
    },
  },
})
