import { createMemoryHistory, createRouter } from 'vue-router'

import Main from "./Main.vue"
import Controllers from "./Controllers.vue"
import StageStatus from "@/components/stageStatus.vue";
import Assembly3D from "@/components/Assembly3D.vue";

const routes = [
  { path: '/', component: Main },
  { path: '/controllers', component: Controllers },
  { path: '/stages', component:StageStatus},
  { path: '/Assembly3D', component: Assembly3D },
]

const router = createRouter({
  history: createMemoryHistory(),
  routes,
})

export default router