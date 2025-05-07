<script setup lang="ts">
// add in websockets connection
// create components that represent controllers
import {ref} from "vue";
import SMC5 from "./components/smc5.vue"
import C884 from "./components/c884.vue"

let smc5objects = ref(new Array<Object>())
let c884objects = ref(new Array<Object>())

</script>

<template>
  <h1>Standa SMC5:</h1>
  <SMC5 v-for="x in smc5objects" :model="x" :key="x.id"/>

  <h1> PI C884: </h1>
  <C884 v-for="x in c884objects" :model="x" :key="x.id"/>

</template>

<style scoped>

</style>