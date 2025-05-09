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



const ws = new WebSocket('/ws/');

ws.onopen = () => {
  console.log('Connected to server');
  // Send the ping!
  ws.send(JSON.stringify({"request":"ping"}))
};

ws.onmessage = (event) => {
  console.log(`Message from server: ${event.data}`);
  try{
    const parsed = JSON.parse(event.data)
    console.log(parsed)
  }catch(e){
    console.log("Error parsing to JSON" + e)
  }
};

ws.onclose = () => {
  console.log('Connection closed');
};
