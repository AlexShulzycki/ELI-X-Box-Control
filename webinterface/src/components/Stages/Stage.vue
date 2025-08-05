<script setup lang="ts">

import {type FullState, useStageStore} from "@/stores/StageStore.ts";
import {ref} from "vue";

const {identifier} = defineProps<{ identifier:number }>()
const stageStore = useStageStore()

const state = ref<FullState|undefined>(stageStore.serverStages.get(identifier))

if(identifier != state.value?.identifier){
  throw Error("key does not match value identifier, something went horribly wrong")
}


function moveBy(offset: number){

}
function moveTo(target: number){}


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
  <h5 v-else>Unknown Stage with ID {{identifier}}</h5>
</template>

<style scoped>

</style>