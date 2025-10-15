<script setup lang="ts">

import {type FullState, type moveStageResponse, useStageStore} from "@/stores/StageStore.ts";
import {computed, ref} from "vue";

const {id} = defineProps<{ id?:number }>()
const emit = defineEmits(['changetree'])

const stageStore = useStageStore()
let res = ref<moveStageResponse>({success: true})
const idselect = ref(id)
const offset = ref(1)

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
  <v-card v-if="state !== undefined"  width="auto" max-width="25%" text-no-wrap>
    <v-card-item v-if="!res.success">
      Error: {{res.error}}
    </v-card-item>
    <v-card-title>ID: {{state.identifier}}</v-card-title>
    <v-card-text>Connected: {{state.connected}}</v-card-text>
    <v-card-text>Ready: {{state.ready}}</v-card-text>
    <v-card-text>Type: {{state.kind}}</v-card-text>
    <v-card-text>Min-Max: {{state.minimum}}mm - {{state.maximum}}mm</v-card-text>
    <v-card-text><b>On Target? {{state.ontarget}}</b></v-card-text>
    <v-card-item>
        <v-row>
          <v-col></v-col>
          <v-col><h6>Position</h6></v-col>
          <v-col></v-col>
        </v-row>
        <v-row>
          <v-col><v-btn @click="moveBy(-offset)">Decrease</v-btn></v-col>
          <v-col>{{state.position}}</v-col>
          <v-col><v-btn @click="moveBy(offset)">Increase</v-btn></v-col>
        </v-row>

    </v-card-item>
  </v-card>
  <div v-else>
    ID: <select v-model="idselect" @change="$emit('changetree', {id: idselect})"> <option v-for="ident in stageStore.getStageIDs">{{ident}}</option> </select>
  </div>
</template>

<style scoped>

</style>