<script setup lang="ts">


import {type WindowGrid} from "@/stores/LayoutStore.ts";

const {windowgrid} = defineProps<{ windowgrid: WindowGrid }>();


function saveLayout(){
  window.alert('implement pls')
}

function switchOrientation(){
  console.log("switchOrientation")
}

function removeSelf(which: number){
  windowgrid.components[which] = ["empty", {}]
}

</script>

<template>
  <div class="options">
    <button @click="saveLayout()">Save Layout</button>
    <button @click="switchOrientation()">Switch Orientation</button>

  </div>
  <div class="windowgrid">
    <div v-if="windowgrid.components[0][0] != 'empty'" class="one">
      <button @click="removeSelf(0)">Remove</button>
      <component v-bind:is="windowgrid.components[0][0]" v-bind="windowgrid.components[0][1]"/>
    </div>
    <div v-if="windowgrid.components[1][0] != 'empty'" class="two">
      <button @click="removeSelf(1)">Remove</button>
      <component v-bind:is="windowgrid.components[1][0]" v-bind="windowgrid.components[0][1]"/>
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