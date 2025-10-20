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
    {path: '/', name: "Home", component: Main},
    {path: '/stages', name: "Stages", component: Stages},
    //{path: '/Assembly3D', name: "Assembly3d", component: Assembly3D},
    //{path: '/AssemblyEditor', name: "AssemblyEditor", component: AssemblyEditor},
    {path: "/HardwareConfig", component: Settings},
    {path: '/XES', children: [
            {path: "/XES/fine-alignment", name:"Fine Alignment", component: XesFineAlignment},
            {path: "/XES/setup", name:"Setup", component: XES_setup},
            {path: "/XES/calculator", name:"Calculator", component: XES_calculator},

        ]
    }

]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

export default router