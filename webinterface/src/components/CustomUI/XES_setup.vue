<script setup lang="ts">


import {reactive, watch} from "vue";

import {useStageStore} from "@/stores/StageStore.ts";
const stageStore = useStageStore()

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
})

function selectID (event, key) {
  console.log("onchange", event.target.value, key)
  localStorage.setItem(key, String(event.target.value))
}


</script>

<template>
  <div>
    <div v-for="[key, id] in axis_ids">
      <h3>
        {{ key }}
      </h3>
      <select @change="selectID($event, key)">
        <option selected v-if="id == 0 || id == undefined">None</option>
        <option v-for="[ident, fullstate] in stageStore.serverStages" :value="ident">{{fullstate.identifier}}: {{fullstate.model}}</option>
      </select>
    </div>
  </div>
</template>

<style scoped>

</style>