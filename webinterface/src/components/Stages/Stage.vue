<script setup lang="ts">

import {type FullState, type moveStageResponse, useStageStore} from "@/stores/StageStore.ts";
import {computed, ref} from "vue";

const {id} = defineProps<{ id?:number }>()
const emit = defineEmits(['changetree'])

const stageStore = useStageStore()
let res = ref<moveStageResponse>({success: true})
const idselect = ref(id)

function moveBy(offset: number){
  stageStore.stepStage(idselect.value, offset).then((value)=>{
    if(value != undefined){
      res.value = value
    }
  })
}
function moveTo(target: number){
  stageStore.moveStage(idselect.value, target).then((value)=>{
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

const state = computed(()=>{

  if(idselect.value != undefined){
    return stageStore.serverStages.get(parseInt(idselect.value))
  }
})

</script>

<template>
  <div v-if="state !== undefined" >
    <div v-if="!res.success">
      Error: {{res.error}}
    </div>
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
          <td><button @click="moveBy(-40)">Decrease</button></td>
          <td>{{state.position}}</td>
          <td><button @click="moveBy(40)">Increase</button></td>
        </tr>
        </tbody>
      </table>

    </div>
  </div>
  <div v-else>
    ID: <select v-model="idselect" @change="$emit('changetree', {id: idselect})"> <option v-for="ident in stageStore.getStageIDs">{{ident}}</option> </select>
  </div>
</template>

<style scoped>

</style>