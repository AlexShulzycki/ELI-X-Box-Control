<script setup lang="ts">
import {useStageStore} from "@/stores/StageStore.ts";
import StepButton from "@/components/Stages/StepButton.vue";
import {ref} from "vue";

const {x, y} = defineProps<{
  x?: number,
  y?: number
}>();
const stageStore = useStageStore();

const step = ref(1)

</script>

<template>
  <div class="container">
  <!--Spawn appropriate buttons, else display message-->
  <div v-if="x!= undefined" class="button" style="grid-column: 1; grid-row: 2"><StepButton v-bind:stageid="x" :direction="0" v-bind:stepby="step"/></div>

  <div v-if="x!= undefined" class="button" style="grid-column: 3; grid-row: 2"><StepButton v-bind:stageid="x" :direction="1" v-bind:stepby="step"/></div>

  <div v-if="y!= undefined" class="button" style="grid-column: 2; grid-row: 1"><StepButton v-bind:stageid="y" :direction="2" v-bind:stepby="step"/></div>

  <div v-if="y!= undefined" class="button" style="grid-column: 2; grid-row: 3"><StepButton v-bind:stageid="y" :direction="3" v-bind:stepby="step"/></div>
</div>
</template>

<style scoped>
.container {
  display: grid;
  width: 100%;
  aspect-ratio: 1;
  background-color: darkgrey;
}
</style>