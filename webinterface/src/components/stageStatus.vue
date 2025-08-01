<script setup lang="ts">
import { useStageStore} from "@/stores/StageStore.ts";
const StageInterface = useStageStore();

</script>

<template>
<button @click="StageInterface.syncAll()">Sync stage status from server</button>
  <button @click="StageInterface.updateStageInfo();StageInterface.updateStageStatus();">Update statuses from server</button>/

  <li v-for="val in StageInterface.getStatusInfoPairs.entries()">
    <p v-if="val[1].info != undefined">{{val[1].info}}</p>
    <p v-if="val[1].status != undefined">{{val[1].status}}</p>
  </li>

</template>

<style scoped>

</style>