<script setup lang="ts">
import {useStageStore} from "@/stores/StageStore.ts";
import Stage from "@/components/Stages/Stage.vue";

const StageInterface = useStageStore();

</script>

<template>
  <v-container>
  <v-toolbar>
    <v-btn @click="StageInterface.syncServerStageInformation(); StageInterface.updateStageInfo()">Refresh</v-btn>
  </v-toolbar>

  <Stage v-for="(stage, key) in StageInterface.serverStages" v-bind:id="stage[1].identifier" :key="key"/>
</v-container>

</template>

<style scoped>

</style>