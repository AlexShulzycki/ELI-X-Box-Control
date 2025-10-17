<script setup lang="ts">

import {useStageStore} from "@/stores/StageStore.ts";
import {ref} from "vue";

const {stageid, reversed = false, direction, stepby} = defineProps<{
  stageid: number,
  reversed?: boolean
  direction: number // 0: left, 1: right, 2: up, 3: down
  stepby: number
}>();

const icons = ["mdi-arrow-left", "mdi-arrow-right", "mdi-arrow-up", "mdi-arrow-down"]

const stageStore = useStageStore();

function step() {
  console.log("stepping stage by step", stageid, stepby)
  if (reversed) {
    stageStore.stepStage(stageid, stepby * -1)
  } else {
    stageStore.stepStage(stageid, stepby)
  }
}

</script>

<template>
  <v-container class="fill-height">
    <v-btn v-if="stageStore.serverStages.get(stageid) != undefined" class="arrow" @click="step()"
    :class="{onTarget: stageStore.serverStages.get(stageid)?.ontarget}">
    <v-icon :icon="icons[direction]"></v-icon>
    </v-btn>
  </v-container>

</template>

<style scoped>
.arrow{
  margin: auto;
  height: 100%;
  aspect-ratio:1;
}
.onTarget {
  background-color: #00ff00;
}
</style>