import {fileURLToPath, URL} from 'node:url'

import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// fonts and other plugins
import ViteFonts from 'unplugin-fonts/vite'
import {templateCompilerOptions} from '@tresjs/core'

// https://vite.dev/config/
export default defineConfig({
    plugins: [
        vue({...templateCompilerOptions}),
        vueDevTools(),
        ViteFonts({
            fontsource: {
                families: [
                    {
                        name: 'Roboto',
                        weights: [100, 300, 400, 500, 700, 900],
                        styles: ['normal', 'italic'],
                    },
                ],
            },
        })
    ],
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url))
        },
    },
    optimizeDeps: {
        // Exclude vuetify since it has an issue with vite dev - TypeError: makeVExpansionPanelTextProps is not a function - the makeVExpansionPanelTextProps is used before it is defined
        exclude: ['vuetify'],
    },
    server: {
        proxy: {
            // With options:
            // http://localhost:5173/api/users
            //   -> http://localhost:5815/users
            '/get': {
                target: 'http://127.0.0.1:8000',
                //changeOrigin: true,
            },
            '/stage': {
                target: 'http://127.0.0.1:8000',
                //changeOrigin: true,
            },
            '/post': {
                target: 'http://127.0.0.1:8000',
                //changeOrigin: true,
            },
            '/ws': {
                target: 'ws://127.0.0.1:8000',
                //changeOrigin: true
            },
        },
    },
    build:{
        outDir: '../server/static',
        emptyOutDir: true,
    }
})
