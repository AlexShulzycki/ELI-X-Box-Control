<script setup lang="ts">

import {type FullState, type moveStageResponse, useStageStore} from "@/stores/StageStore.ts";
import {ref} from "vue";

const {state} = defineProps<{ state:FullState }>()
const stageStore = useStageStore()

let res = ref<moveStageResponse>({success: true})

function moveBy(offset: number){
  stageStore.stepStage(state.identifier, offset).then((value)=>{
    if(value != undefined){
      res.value = value
    }
  })
}
function moveTo(target: number){
  stageStore.moveStage(state.identifier, target).then((value)=>{
    if(value != undefined){
      res.value = value
    }
  })
}

function processResponse(res: moveStageResponse){
  if(!res.success){
    window.alert(res.error)
  }
}

</script>

<template>
  <div v-if="state !== undefined">
    <h5>ID: {{state.identifier}}</h5>
    <p>Connected: {{state.connected}}</p>
    <p>Ready: {{state.ready}}</p>
    <p>Type: {{state.kind}}</p>
    <p>Min-Max: {{state.minimum}}mm - {{state.maximum}}mm</p>
    <p><b>On Target? {{state.ontarget}}</b></p>
    <div>
      <table>
        <tbody>
        <tr>
          <th></th>
          <th><h6>Position</h6></th>
          <th></th>
        </tr>
        <tr>
          <td><button @click="moveBy(-1)">Decrease</button></td>
          <td>{{state.position}}</td>
          <td><button @click="moveBy(1)">Increase</button></td>
        </tr>
        </tbody>
      </table>

    </div>
  </div>
</template>

<style scoped>

</style>