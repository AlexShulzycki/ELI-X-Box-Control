<script setup lang="ts">
import ConfigBrowser from "@/components/ConfigBrowser.vue";
import {useConfigurationStore} from "@/stores/ConfigurationState.ts";

const config = useConfigurationStore()
</script>

<template>
  <h1>Beautiful settings tab (in progress)</h1>
<ConfigBrowser
    v-for="key in config.configSchemas.keys()"
    v-bind:config_type_key="key"
/>
</template>

<style scoped>

</style>