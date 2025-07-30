<script async setup lang="ts">

import {useConfigurationStore} from "@/stores/ConfigurationState.ts";

const configs = useConfigurationStore()

function run_debug(){
  configs.syncConfigSchema()
  configs.syncServerConfigState()
}

</script>

<template>
<h1>This is the main page</h1>

  <button @click="run_debug()">The magical debug button</button>
</template>

<style scoped>

</style>