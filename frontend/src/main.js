import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import VueViewer from 'v-viewer'
import 'viewerjs/dist/viewer.css'
import App from './App.vue'
import router from './router'
import './style.css'

const app = createApp(App)
app.use(router)
app.use(createPinia())
app.use(ElementPlus)
app.use(VueViewer, { defaultOptions: { zIndex: 9999 } })
app.mount('#app')
