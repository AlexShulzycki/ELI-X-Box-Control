import './assets/main.css'
import {createApp} from 'vue'
import {createPinia} from 'pinia'
import router from './router'
import App from './App.vue'

import Stage from "@/components/Stages/Stage.vue";
import Assembly3D from "@/components/3D/Assembly3D.vue";
import WindowGrid from "@/components/Layout/WindowGrid.vue";

// Vuetify
import 'vuetify/styles'
import {createVuetify} from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

// Fonts??
import 'unfonts.css'
import { mdi, aliases as mdiAliases } from 'vuetify/iconsets/mdi';
import { mdiIconAliases } from '@jsonforms/vue-vuetify';
import '@mdi/font/css/materialdesignicons.css'


const pinia = createPinia()
const app = createApp(App)
app.use(router)
app.use(pinia)

// Registering components for the windowgrid
app.component("WindowGrid", WindowGrid)
app.component("Stage", Stage)
app.component("Assembly3D", Assembly3D)

app.mount('#app')

//vuetify
const vuetify = createVuetify({
    components,
    directives,
    icons: {
        defaultSet: 'mdi',
        sets: {
            mdi,
        },
        aliases: {...mdiAliases, ...mdiIconAliases},
    }
})

app.use(vuetify)


// WEBSOCKET HANDLING BELOW, WE DO IT HERE BECAUSE PINIA IS FIDDLY, HERE WE KNOW FOR SURE
// THAT IT IS INSTANTIATED AND READY TO USE

import {
    useStageStore,
    type StageStatus,
    type StageInfo,
    type StageRemoved
} from "@/stores/StageStore.ts";


const stagestore = useStageStore();

class WSClient {

    constructor(private ws: WebSocket) {
        this.ws = ws

        ws.onopen = () => {
            console.log('Connected to server');
        }

        ws.onmessage = (event) => {
            console.log(`Message from server: ${event.data}`);
            try {
                const parsed = <WSMessage>JSON.parse(event.data)
                this.receive(parsed)
            } catch (e) {
                console.log("Error parsing to JSON" + e)
            }
        }

        ws.onclose = () => {
            console.log('Connection closed');
        }
    }

    receive(message: WSMessage) {
        console.log("receiving WSMessage", message)
        if (message.event == "StageStatus") {
            // try parse it
            try {
                const msg = JSON.parse(message.data) as StageStatus
                stagestore.receiveStageStatus(msg)
            } catch (e) {
                console.log(e)
            }
        } else if (message.event == "StageInfo") {
            try {
                const msg = JSON.parse(message.data) as StageInfo
                console.log(typeof msg)
                stagestore.receiveStageInfo(msg)
            } catch (e) {
                console.log(e)
            }
        } else if (message.event == "StageRemoved") {
            try {
                const msg = JSON.parse(message.data) as StageRemoved
                stagestore.receiveStageRemoved(msg)
            } catch (e) {
                console.log(e)
            }
        }
    }
}

// Start up websocket handling
const wsclient = new WSClient(new WebSocket('/ws/'))

interface WSMessage {
    event: string;
    data: any;
}