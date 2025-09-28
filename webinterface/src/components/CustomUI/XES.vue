<script setup lang="ts">

import XYControl from "@/components/Stages/XYControl.vue";
import {reactive} from "vue";


const axis_ids = reactive(new Map<string, number>([
  ["crystalx", 0],
  ["crystaly", 0],
  ["detectorx", 0],
  ["detectory", 0],
  ["samplex", 0],
  ["sampley", 0]
]))

// Populate axis_ids from storage, if they are in storage
axis_ids.forEach((value, key, map) => {
  // grab value for the key
  const val = localStorage.getItem(key)
  if (!val) {
    // Not there, prepopulate
    localStorage.setItem(key, "")
  } else {
    // there, lets load
    try {
      map.set(key, Number(val))
    } catch (e) {
      console.log(e)
    }
  }
})

// Update our reactive map when storage changes
window.addEventListener("storage", (e) => {
  if (!e.key || !axis_ids.get(e.key)) {
    // not relevant to us, return
    return
  } else {
    // double check for null values, if so then just put in an empty string
    try {
      if (!e.newValue) {
        return
      } else {
        // update the object
        axis_ids.set(e.key, Number(e.newValue))
      }
    } catch (e) {
      console.log(e)
    }

  }
});

</script>

<template>
  <div style="display: grid; width: 100vw;">
    <div class="info">
      <table>
        <tbody>
        <tr>
          <th>Axis</th>
          <th>Identifier</th>
          <th>Position</th>
          <th>On Target?</th>
          <th>Misc</th>
        </tr>
        <tr v-for="[name,id] in axis_ids" :key="name">
          <td>{{name}}</td>
          <td>{{id}}</td>
          <td>{{}}</td>
        </tr>
        </tbody>
      </table>
    </div>
    <div class="crystal">
      <XYControl v-bind:x="axis_ids.get('crystalx')" v-bind:y="axis_ids.get('crystaly')" label="Crystal"/>
    </div>
    <div class="detector">
      <XYControl v-bind:x="axis_ids.get('detectorx')" v-bind:y="axis_ids.get('detectory')" label="Detector"/>
    </div>
    <div class="sample">
      <XYControl v-bind:x="axis_ids.get('samplex')" v-bind:y="axis_ids.get('sampley')" label="Sample"/>
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