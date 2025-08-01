<script setup lang="ts">
import VirtualConfigBrowser from "@/components/ConfigComponents/Virtual/VirtualConfigBrowser.vue";
import {useConfigurationStore} from "@/stores/ConfigurationStore.ts";
import PIConfigBrowser from "@/components/ConfigComponents/PI/PIConfigBrowser.vue";

const config = useConfigurationStore()
</script>

<template>
  <h1>Beautiful settings tab (in progress)</h1>
  <div v-for="key in config.configSchemas.keys()">
    <VirtualConfigBrowser v-if="key == 'Virtual'"/>
    <PIConfigBrowser v-else-if="key == 'PI'"/>
    <h4 v-else>Schema {{key}} does not have a settings page implemented yet.</h4>
  </div>

</template>

<style scoped>

</style>