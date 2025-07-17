<script setup lang="ts">
import { useStageInterfaceStore} from "@/stores/StageInterfaceState.ts";
const StageInterface = useStageInterfaceStore();
</script>

<template>
<button @click="StageInterface.syncAll()">Sync stage status from server</button>
  <button @click="StageInterface.updateStageInfo();StageInterface.updateStageStatus();">Update statuses from server</button>/
</template>

<style scoped>

</style>