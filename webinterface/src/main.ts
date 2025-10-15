import './assets/main.css'
import {createApp} from 'vue'
import {createPinia} from 'pinia'
import router from './router'
import App from './App.vue'

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
//app.component("WindowGrid", WindowGrid)
//app.component("Stage", Stage)
//app.component("Assembly3D", Assembly3D)


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


app.mount('#app')


// WEBSOCKET HANDLING BELOW, WE DO IT HERE BECAUSE PINIA IS FIDDLY, HERE WE KNOW FOR SURE
// THAT IT IS INSTANTIATED AND READY TO USE

import {
    useStageStore,
    type StageStatus,
    type StageInfo,
    type StageRemoved
} from "@/stores/StageStore.ts";
import {type ConfigurationUpdate, useConfigurationStore} from "@/stores/ConfigurationStore.ts";
import {useSettingsStore} from "@/stores/SettingsStore.ts";


const stagestore = useStageStore();
const configstore = useConfigurationStore();
const settingsStore = useSettingsStore();

class WSClient {

    constructor(private ws: WebSocket) {
        this.ws = ws
        this.init_ws_behavior()

        // check if we are even connected in the first place, try again otherwise.
        // we do this because if we fail to connect on startup, the onclose function does not trigger.
        if(this.ws.readyState === WebSocket.CLOSED) {
            this.ws = new WebSocket(this.ws.url)
            this.init_ws_behavior()
        }

    }

    init_ws_behavior(){
        // assign functions to the new websocket
        this.ws.onopen = () => {
            console.log('Connected to server');
            // update the state
            settingsStore.websocketConnected = true
        }

        this.ws.onmessage = (event) => {
            console.log(`Message from server: ${event.data}`);
            try {
                const parsed = <WSMessage>JSON.parse(event.data)
                this.receive(parsed)
            } catch (e) {
                console.log("Error parsing to JSON" + e)
            }
        }

        this.ws.onclose = () => {
            console.log('Connection closed');
            // update the state
            settingsStore.websocketConnected = false
            // try to reconnect
            setTimeout(function(wsclient: WSClient){
                // extract the current url
                const url = wsclient.ws.url
                // create a new websocket
                wsclient.ws = new WebSocket(url)
                // give it the proper functions it needs
                wsclient.init_ws_behavior()
            }, 500, this)

        }
    }

    receive(message: WSMessage) {
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
        } else if (message.event == "ConfigurationUpdate") {
            try{
                // update specific configuration
                configstore.newConfigurationUpdate(message.data as ConfigurationUpdate)

            }catch (e) {
                console.log("configuration update error", e)
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