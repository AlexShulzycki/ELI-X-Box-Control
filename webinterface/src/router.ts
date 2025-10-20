import {createMemoryHistory, createRouter, createWebHistory} from 'vue-router'

import Main from "./Main.vue"
import Stages from "@/components/Stages.vue";
import Assembly3D from "@/components/3D/Assembly3D.vue";
import AssemblyEditor from "@/components/AssemblyViewer/AssemblyEditor.vue";

import XesFineAlignment from "@/components/CustomUI/XES/XES_fine_alignment.vue"
import XES_setup from "@/components/CustomUI/XES/XES_setup.vue";
import XES_calculator from "@/components/CustomUI/XES/XES_calculator.vue";
import Settings from "@/components/Settings.vue";

const routes = [
    {path: '/', component: Main},
    {path: '/stages', component: Stages},
    {path: '/Assembly3D', component: Assembly3D},
    {path: '/AssemblyEditor', component: AssemblyEditor},
    {path: "/XES", component: XesFineAlignment},
    {path: "/XES_setup", component: XES_setup},
    {path: "/XES_calculator", component: XES_calculator},
    {path: "/HardwareConfig", component: Settings}
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

export default router