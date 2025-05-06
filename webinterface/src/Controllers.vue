<script setup lang="ts">
// add in websockets connection
// create components that represent controllers
import {ref} from "vue";
import SMC5 from "./components/smc5.vue"
import C884 from "./components/c884.vue"

const ws = new WebSocket('/ws/');

let smc5objects = ref(new Array<Object>())
let c884objects = ref(new Array<Object>())

ws.onopen = () => {
  console.log('Connected to server');
  // Send the ping!
  ws.send("{'ping':'ping!'}")
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

</script>

<template>
  <h1>Standa SMC5:</h1>
  <SMC5 v-for="x in smc5objects" :model="x" :key="x.id"/>

  <h1> PI C884: </h1>
  <C884 v-for="x in c884objects" :model="x" :key="x.id"/>

</template>

<style scoped>

</style>