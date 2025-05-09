<script setup lang="ts">
// add in websockets connection
// create components that represent controllers
import {ref} from "vue";
import SMC5 from "./components/smc5.vue"
import C884 from "./components/c884.vue"

import {useAxisStore, C884Controller, SMC5Controller} from "@/stores/AxisState.ts";
const AxesStore = useAxisStore()

let controllers = AxesStore.getControllers

let smc5objects = ref(controllers["SMC5"])
let c884objects = ref(controllers["C884"])

</script>

<template>
  <button @click="AxesStore.overwriteFromSettings()"> Fetch settings</button>

  <h1>Standa SMC5:</h1>
  <SMC5 v-for="x in smc5objects" :model="x"/>

  <h1> PI C884: </h1>
  <button @click="">Add a C884 Controller</button>
  <C884 v-for="x in c884objects" :controller="x" :key="x.comport"/>




</template>

<style scoped>

</style>