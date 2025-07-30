import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import router from './router'
import App from './App.vue'

const pinia = createPinia()
const app = createApp(App)
app.use(router)
app.use(pinia)

app.mount('#app')


// WEBSOCKET HANDLING BELOW, WE DO IT HERE BECAUSE PINIA IS FIDDLY, HERE WE KNOW FOR SURE
// THAT IT IS INSTANTIATED AND READY TO USE

import {
    useStageInterfaceStore,
    type StageStatus,
    type StageInfo,
    type StageRemoved
} from "@/stores/StageInterfaceState.ts";
const stagestore = useStageInterfaceStore();

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
        if(message.event == "StageStatus"){
            // try parse it
            try{
                const msg = JSON.parse(message.data) as StageStatus
                stagestore.receiveStageStatus(msg)
            }catch(e){
                console.log(e)
            }
        }else if(message.event == "StageInfo"){
            try{
                const msg = JSON.parse(message.data) as StageInfo
                console.log(typeof msg)
                stagestore.receiveStageInfo(msg)
            }catch(e){
                console.log(e)
            }
        }else if(message.event == "StageRemoved"){
            try{
                const msg = JSON.parse(message.data) as StageRemoved
                stagestore.receiveStageRemoved(msg)
            }catch(e){
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