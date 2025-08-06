<script setup lang="ts">


import {type WindowGrid} from "@/stores/LayoutStore.ts";
import {ref, resolveComponent} from "vue";

const {windowgrid} = defineProps<{ windowgrid: WindowGrid }>();

// Initialize the components in this window grid

const one = (windowgrid.components[0][0] != "empty")? ref(resolveComponent(windowgrid.components[0][0])): ref("empty")
const two = (windowgrid.components[1][0] != "empty")? ref(resolveComponent(windowgrid.components[1][0])): ref("empty")


function saveLayout(){
  window.alert('implement pls')
}

function switchOrientation(){
  console.log("switchOrientation")
}

function removeSelf(){
  console.log("removeSelf")
}

</script>

<template>
  <div class="options">
    <button @click="saveLayout()">Save Layout</button>
    <button @click="switchOrientation()">Switch Orientation</button>
    <button @click="removeSelf()">Remove</button>
  </div>
  <div class="windowgrid">
    <div v-if="one == 'empty'" class="one">
      <one v-bind="windowgrid.components[0][1]"/>
    </div>
    <div v-if="two == 'empty'" class="two">
      <two v-bind="windowgrid.components[1][1]"/>
    </div>
  </div>
</template>

<style scoped>

template {
  width: 100%;
  height: 100%;
}

.windowgrid {
  display: grid;
  width: 100%;
  height: 100%;
}

</style>