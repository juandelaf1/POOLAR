import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Proxy dev: /api -> FastAPI (POOLAR). Ajusta target si tu backend corre en otro puerto.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
