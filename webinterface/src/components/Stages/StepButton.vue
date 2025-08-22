<script setup lang="ts">

import {useStageStore} from "@/stores/StageStore.ts";

const {stageid, negative = false, direction, stepby} = defineProps<{
  stageid: number,
  negative?: boolean
  direction: number // 0: left, 1: right, 2: up, 3: down
  stepby: number
}>();

const stageStore = useStageStore();

const stage = stageStore.serverStages.get(stageid)

function step(){
  console.log("stepping stage by step", stageid, stepby)
}

</script>

<template>

</template>

<style scoped>

</style>