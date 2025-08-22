<script setup lang="ts">

import {useStageStore} from "@/stores/StageStore.ts";
import Stage from "@/components/Stages/Stage.vue";
import XYControl from "@/components/Stages/XYControl.vue";

const {crystalx, crystaly, detectorx, detectory, samplex, sampley} = defineProps<{
  crystalx: number,
  crystaly: number,
  detectorx: number,
  detectory: number,
  samplex: number,
  sampley: number
}>();

const stagestore = useStageStore();
// grab the stage information from the stage store
const stageCrystalX = stagestore.serverStages.get(crystalx)
const stageCrystalY = stagestore.serverStages.get(crystaly)

const stageDetectorX = stagestore.serverStages.get(detectorx)
const stageDetectorY = stagestore.serverStages.get(detectory)

const stageSampleX = stagestore.serverStages.get(samplex)
const stageSampleY = stagestore.serverStages.get(sampley)

</script>

<template>
  <div style="display: grid; width: 100vw;">
    <div class="info">
      info blah blah blah
    </div>
    <div class="crystal">
      crystal
      <XYControl v-bind:x="crystalx" v-bind:y="crystaly"/>
    </div>
    <div class="detector">
      detector
      <XYControl v-bind:x="detectorx" v-bind:y="detectory"/>
    </div>
    <div class="sample">
      sample
      <XYControl v-bind:x="samplex" v-bind:y="sampley"/>
    </div>
  </div>
</template>

<style scoped>

.info {
  grid-column: 1;
  grid-row: 1;
}

.crystal {
  grid-column: 2;
  grid-row: 1;
}

.detector {
  grid-column: 3;
  grid-row: 2;
}

.sample {
  grid-column: 1;
  grid-row: 2;
}

</style>