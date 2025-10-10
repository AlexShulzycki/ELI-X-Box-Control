<script setup lang="ts">
import {useStageStore} from "@/stores/StageStore.ts";
import StepButton from "@/components/Stages/StepButton.vue";
import {ref} from "vue";

const {x, xrev=false, y, yrev=false} = defineProps<{
  x?: number,
  xrev?: boolean,
  y?: number,
  yrev?: boolean,
  label?: string,
}>();

const step = ref(1)

</script>

<template>
  <div class="container">
    <!--Spawn appropriate buttons, else display message
    Directions - 0: left, 1: right, 2: up, 3: down
    -->
    <StepButton v-if="x!= undefined" style="grid-column: 1; grid-row: 2" v-bind:stageid="x" :direction="0"
                v-bind:stepby="-step" v-bind:reversed="xrev"/>

    <StepButton v-if="x!= undefined" style="grid-column: 3; grid-row: 2" v-bind:stageid="x" :direction="1"
                v-bind:stepby="step" v-bind:reversed="xrev"/>

    <StepButton v-if="y!= undefined" style="grid-column: 2; grid-row: 1" v-bind:stageid="y" :direction="2"
                v-bind:stepby="step" v-bind:reversed="yrev"/>

    <StepButton v-if="y!= undefined" style="grid-column: 2; grid-row: 3" v-bind:stageid="y" :direction="3"
                v-bind:stepby="-step" v-bind:reversed="yrev"/>

    <div style="grid-column: 2; grid-row: 2; text-align: center">
      <h3 v-if="label != undefined">{{ label }}</h3>
      <h4>Step size (mm)</h4>
      <input v-model="step" style="width: 50%"/>
    </div>
  </div>
</template>

<style scoped>
.container {
  display: grid;
  grid-auto-columns: minmax(0, 1fr);
  grid-auto-flow: column;
  width: 60%;
  margin: auto;
  aspect-ratio: 1;
  background-color: darkgrey;
}
</style>