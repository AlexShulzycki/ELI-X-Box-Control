import { createMemoryHistory, createRouter } from 'vue-router'

import Main from "./Main.vue"
import Stages from "@/components/Stages.vue";
import Assembly3D from "@/components/3D/Assembly3D.vue";
import AssemblyEditor from "@/components/AssemblyViewer/AssemblyEditor.vue";

import XES from "@/components/CustomUI/XES.vue"
import XES_setup from "@/components/CustomUI/XES_setup.vue";

const routes = [
  { path: '/', component: Main },
  { path: '/stages', component:Stages},
  { path: '/Assembly3D', component: Assembly3D },
  { path: '/AssemblyEditor', component: AssemblyEditor },
  { path: "/XES", component: XES },
    { path: "/XES_setup", component: XES_setup },
]

const router = createRouter({
  history: createMemoryHistory(),
  routes,
})

export default router