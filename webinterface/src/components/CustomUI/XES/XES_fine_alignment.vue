<script setup lang="ts">

import XYControl from "@/components/Stages/XYControl.vue";
import {reactive} from "vue";
import {load_prepopulate, type localAxisSetting, updateMapFromStorage} from "@/components/CustomUI/XES/xes.ts";
import {useStageStore} from "@/stores/StageStore.ts";


const stageStore = useStageStore();

const axes = reactive(new Map<string, localAxisSetting>())

// load and or prepopulate
load_prepopulate(axes)

// Update our reactive map when storage changes
window.addEventListener("storage", (e) => {
  console.log("listener event")
  updateMapFromStorage(e, axes)
})

</script>

<template>
  <div style="display: grid; width: 100vw;">
    <div class="info">
      <table>
        <tbody>
        <tr>
          <th>Axis</th>
          <th>Identifier</th>
          <th>Model</th>
          <th>Position (mm)</th>
          <th>On Target?</th>
          <th>Misc</th>
        </tr>
        <tr v-for="[name,state] in axes" :key="name">
          <td>{{name}}</td>
          <td>{{state.identifier}}</td>
          <td>{{stageStore.serverStages.get(state.identifier)?.model}}</td>
          <td>{{stageStore.serverStages.get(state.identifier)?.position}}</td>
          <td>{{stageStore.serverStages.get(state.identifier)?.ontarget}}</td>
          <td v-if="!stageStore.serverStages.get(state.identifier)">Disconnected</td>
          <td v-else>{{state.reversed? "Reversed": ""}}</td>
        </tr>
        </tbody>
      </table>
    </div>
    <div class="crystal">
      <XYControl v-bind:x="axes.get('crystalx')?.identifier" v-bind:y="axes.get('crystaly')?.identifier" label="Crystal"
      v-bind:xrev="axes.get('crystalx')?.reversed" v-bind:yrev="axes.get('crystaly')?.reversed"/>
    </div>
    <div class="detector">
      <XYControl v-bind:x="axes.get('detectorx')?.identifier" v-bind:y="axes.get('detectory')?.identifier" label="Detector"
      v-bind:xrev="axes.get('detectorx')?.reversed" v-bind:yrev="axes.get('detectory')?.reversed"/>
    </div>
    <div class="sample">
      <XYControl v-bind:x="axes.get('samplex')?.identifier" v-bind:y="axes.get('sampley')?.identifier" label="Sample"
      v-bind:xrev="axes.get('samplex')?.reversed" v-bind:yrev="axes.get('sampley')?.reversed"/>
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

table, th, td{
  text-align: center;
  border: 2px solid black;
  border-collapse: collapse;
  padding: 5px;
}
tr:nth-child(even) {
  background-color: #D6EEEE;
}


</style>