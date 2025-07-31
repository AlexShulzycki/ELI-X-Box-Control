<script setup lang="ts">
import { useStageStore} from "@/stores/StageStore.ts";
const StageInterface = useStageStore();
</script>

<template>
<button @click="StageInterface.syncAll()">Sync stage status from server</button>
  <button @click="StageInterface.updateStageInfo();StageInterface.updateStageStatus();">Update statuses from server</button>/

  <li v-for="stage in StageInterface.stageInfo.values()">
    <p>{{ stage.kind }} stage, model {{ stage.model }} with identifier {{ stage.identifier }}. Position:
      {{ StageInterface.stageStatus.get(stage.identifier)?.position }}</p>
  </li>

</template>

<style scoped>

</style>