<script setup lang="ts">

import {useStageStore} from "@/stores/StageStore.ts";
import {ref} from "vue";

const {stageid, reversed = false, direction, stepby} = defineProps<{
  stageid: number,
  reversed?: boolean
  direction: number // 0: left, 1: right, 2: up, 3: down
  stepby: number
}>();

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
  <div style="padding: 25%; border-radius:30%; margin: 10%" :class="{onTarget: stageStore.serverStages.get(stageid)?.ontarget}">
    <div v-if="stageStore.serverStages.get(stageid) != undefined" class="arrow"
         :class="{left: direction == 0, right: direction == 1, up: direction==2, down: direction == 3}"
         @click="step()">

    </div>
  </div>

</template>

<style scoped>


.arrow {
  border: solid black;
  border-width: 0 3px 3px 0;
  display: inline-block;
  width: 100%;
  aspect-ratio: 1;
  margin-left: auto;
  margin-right: auto;
}

.right {
  transform: rotate(-45deg);
}

.left {
  transform: rotate(135deg);
}

.up {
  transform: rotate(-135deg);
}

.down {
  transform: rotate(45deg);
}

.onTarget {
  background-color: green;
}
</style>