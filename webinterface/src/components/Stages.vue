<script setup lang="ts">
import {useStageStore} from "@/stores/StageStore.ts";
import Stage from "@/components/Stages/Stage.vue";
const StageInterface = useStageStore();

</script>

<template>
<button @click="StageInterface.syncServerStageInformation()">Sync stage status from server</button>
  <button @click="StageInterface.updateStageInfo()">Tell the server to refresh</button>

  <Stage v-for="(stage, key) in StageInterface.serverStages" v-bind:id="stage[1].identifier" :key="key" />

</template>

<style scoped>

</style>