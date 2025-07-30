<script setup lang="ts">
import {useConfigurationStore} from "@/stores/ConfigurationState.ts";
import VirtualConfig from "@/components/ConfigComponents/Virtual/VirtualConfig.vue";
const config = useConfigurationStore();

</script>

<template>
<div class="flex-container">
  <h1>Configuration Browser for Virtual Stages</h1>
    <virtual-config
        v-for="state in config.serverConfigs.get('Virtual')"
        v-bind:state="state"
        :key="state.identifier"
    />
    <button @click="console.log('weewoo')">Add another configuration</button>

</div>
</template>

<style scoped>
.flex-container {
  display: flex;
  flex-direction: column;
}
</style>