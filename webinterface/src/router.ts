import { createMemoryHistory, createRouter } from 'vue-router'

import Main from "./Main.vue"
import Controllers from "./Controllers.vue"

const routes = [
  { path: '/', component: Main },
  { path: '/controllers', component: Controllers },
]

const router = createRouter({
  history: createMemoryHistory(),
  routes,
})

export default router