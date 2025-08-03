import { createMemoryHistory, createRouter } from 'vue-router'

import Main from "./Main.vue"
import Controllers from "./components/Controllers.vue"
import Stages from "@/components/Stages.vue";
import Assembly3D from "@/components/3D/Assembly3D.vue";

const routes = [
  { path: '/', component: Main },
  { path: '/controllers', component: Controllers },
  { path: '/stages', component:Stages},
  { path: '/Assembly3D', component: Assembly3D },
]

const router = createRouter({
  history: createMemoryHistory(),
  routes,
})

export default router