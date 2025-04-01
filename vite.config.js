import { defineConfig } from 'vite'
import vue2 from '@vitejs/plugin-vue2'
import { randomBytes } from 'crypto'

// 改进的 polyfill 实现
if (!global.crypto) {
  global.crypto = {}
}

if (!global.crypto.getRandomValues) {
  global.crypto.getRandomValues = function(array) {
    const randomBytesBuffer = randomBytes(array.length)
    for (let i = 0; i < array.length; i++) {
      array[i] = randomBytesBuffer[i]
    }
    return array
  }
}

export default defineConfig({
  plugins: [vue2()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  }
})