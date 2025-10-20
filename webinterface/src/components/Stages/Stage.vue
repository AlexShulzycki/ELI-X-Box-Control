<script setup lang="ts">

import {type FullState, type moveStageResponse, useStageStore} from "@/stores/StageStore.ts";
import {computed, ref} from "vue";

const {id} = defineProps<{ id?: number }>()
const emit = defineEmits(['changetree'])

const stageStore = useStageStore()
let res = ref<moveStageResponse>({success: true})
const idselect = ref(id)
const offset = ref(1)
const absoluteInput = ref(0)

function moveBy(offset: number) {
  if (idselect.value == undefined) {
    return
  }
  stageStore.stepStage(idselect.value, offset).then((value) => {
    if (value != undefined) {
      res.value = value
    }
  })
}

function moveTo() {
  if (idselect.value == undefined || absoluteInput.value == undefined) return
  stageStore.moveStage(idselect.value, absoluteInput.value).then((value) => {
    if (value != undefined) {
      res.value = value
    }
  })
}

function processResponse(res: moveStageResponse) {
  if (!res.success) {
    window.alert(res.error)
  }
}

const state = computed(() => {

  if (idselect.value != undefined) {
    return stageStore.serverStages.get(idselect.value)
  }
})

</script>

<template>
  <v-card v-if="state !== undefined" width="auto" max-width="25%" text-no-wrap>
    <v-card-item v-if="!res.success">
      Error: {{ res.error }}
    </v-card-item>
    <v-card-title>ID: {{ state.identifier }}</v-card-title>
    <v-card-text>
      {{ state.connected?"Connected":"Disconnected" }} <br>
      {{ state.ready?"Ready":"Not ready" }} <br>
      Type: {{ state.kind }} <br>
      Range from {{ state.minimum }} to {{ state.maximum }} mm <br>
      {{ state.ontarget?"On target" : "Not on target" }}
    </v-card-text>
    <v-card-actions>

        Position
          <v-btn @click="moveBy(-offset)" icon="mdi-minus"/>

        {{ String(Math.round(state.position*100)/100) + "mm"}}

          <v-btn @click="moveBy(offset)" icon="mdi-plus"/>
    </v-card-actions>
    <v-card-actions>
      <br>

      <v-number-input v-model="absoluteInput" :precision="3" control-variant="stacked"/>
      <v-btn @click="moveTo">Set</v-btn>

    </v-card-actions>
  </v-card>
  <div v-else>
    ID: <select v-model="idselect" @change="$emit('changetree', {id: idselect})">
    <option v-for="ident in stageStore.getStageIDs">{{ ident }}</option>
  </select>
  </div>
</template>

<style scoped>

</style>