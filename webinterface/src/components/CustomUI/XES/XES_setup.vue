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

function selectID(event, key: string) {
  let current = getSetting(key)
  if (!current) return
  current.identifier = Number(event.target.value)
  saveSetting(key, current)
}

function setReversed(event, key: string) {
  let current = getSetting(key)
  if (!current) return
  current.reversed = Boolean(event.target.checked)
  saveSetting(key, current)
}

function setOffset(event, key: string) {
  let current = getSetting(key)
  if (!current) return
  current.offset = Number(event.target.value)
  saveSetting(key, current)
}

// Update our reactive map when storage changes
window.onstorage = (e) => {
  updateMapFromStorage(e, axes)
}
</script>

<template>
  <div>
    <table>
      <tbody>
      <tr>
        <th>Axis Name</th>
        <th>Axis Identifier</th>
        <th></th>
        <th>Offset</th>
      </tr>
      <tr v-for="[key, axis] in axes">
        <td>
          <h3>
            {{ key }}
          </h3>
        </td>
        <td>
          <select @change="selectID($event, key)" v-bind:value="axis.identifier">
            <option :value="0">None</option>
            <option v-for="[ident, fullstate] in stageStore.serverStages" :value="ident">{{ fullstate.identifier }}:
              {{ fullstate.model }}
            </option>
          </select>
        </td>
        <td>
          Reversed
          <input type="checkbox" v-bind:value="axis.reversed" @change="setReversed($event, key)"
                 v-bind:checked="axis.reversed">
        </td>
        <td>
          <input type="number" v-bind:value="axis.offset" @change="setOffset($event, key)">
        </td>
      </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>

</style>