<script setup lang="ts">
import {useStageStore} from "@/stores/StageStore.ts";
const StageInterface = useStageStore();

</script>

<template>
<button @click="StageInterface.syncServerStageInformation()">Sync stage status from server</button>
  <button @click="StageInterface.updateStageInfo()">Tell the server to refresh</button>

  <li v-for="[id, val] in StageInterface.serverStages">
    <h4>{{val.identifier}}</h4>
    <h4>{{val.model}}</h4>
    <p v-if="val.connected">Connected</p><p v-else> Disconnected</p>
    <p v-if="val.ready">Ready</p> <p v-else>Not Ready</p>
    <p>{{val.kind}}</p>
    <p>{{val.minimum}} - {{val.maximum}}mm</p>
    <p>Position: {{val.position}}</p>
    <p v-if="val.ontarget">On target</p> <p v-else> Not on target</p>
  </li>

</template>

<style scoped>

</style>