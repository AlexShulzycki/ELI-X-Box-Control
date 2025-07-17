import { createMemoryHistory, createRouter } from 'vue-router'

import Main from "./Main.vue"
import Controllers from "./Controllers.vue"
import StageStatus from "@/components/stageStatus.vue";

const routes = [
  { path: '/', component: Main },
  { path: '/controllers', component: Controllers },
  {path: '/stages', component:StageStatus}
]

const router = createRouter({
  history: createMemoryHistory(),
  routes,
})

export default router