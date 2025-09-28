<script setup lang="ts">


import {reactive, watch} from "vue";
import {
  type localAxisSetting,
  getSetting,
  saveSetting,
  load_prepopulate,
  updateMapFromStorage
} from "@/components/CustomUI/XES/xes.ts";

import {useStageStore} from "@/stores/StageStore.ts";
const stageStore = useStageStore()

const axes = reactive(new Map<string, localAxisSetting>())

// load and or prepopulate
load_prepopulate(axes)

// Update our reactive map when storage changes
window.addEventListener("storage", (e) => {
  updateMapFromStorage(e, axes)
})

function selectID (event, key:string) {
  let current = getSetting(key)
  if(!current) return
  current.identifier = Number(event.target.value)
  saveSetting(key, current)
}

function setReversed(event, key:string){
  let current = getSetting(key)
  if(!current) return
  current.reversed = Boolean(event.target.checked)
  saveSetting(key, current)
}


</script>

<template>
  <div>
    <div v-for="[key, axis] in axes">
      <h3>
        {{ key }}
      </h3>
      <select @change="selectID($event, key)" v-bind:value="axis.identifier">
        <option :value="0">None</option>
        <option v-for="[ident, fullstate] in stageStore.serverStages" :value="ident">{{fullstate.identifier}}: {{fullstate.model}}</option>
      </select>
      Reversed
      <input type="checkbox" v-bind:value="axis.reversed" @change="setReversed($event, key)" v-bind:checked="axis.reversed">
    </div>
  </div>
</template>

<style scoped>

</style>