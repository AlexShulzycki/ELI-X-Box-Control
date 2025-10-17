<script setup lang="ts">
import {useStageStore} from "@/stores/StageStore.ts";
import Stage from "@/components/Stages/Stage.vue";

const StageInterface = useStageStore();

</script>

<template>
<v-sheet width="100%">
  <v-toolbar>
    <v-btn @click="StageInterface.syncServerStageInformation(); StageInterface.updateStageInfo()">Refresh</v-btn>
  </v-toolbar>

    <Stage v-for="(stage, key) in StageInterface.serverStages" v-bind:id="stage[1].identifier" :key="key"/>
  </v-sheet>
</template>

<style scoped>

</style>