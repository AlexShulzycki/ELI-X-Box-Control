<script async setup lang="ts">
// sync settings from server first
import {useSettingsStore} from "@/stores/SettingsStore.ts";
import {useConfigurationStore} from "@/stores/ConfigurationState.ts";

const configs = useConfigurationStore()
const settings = useSettingsStore()

function run_debug(){
  configs.syncConfigSchema()
  configs.syncServerConfigState()
}

try{
  settings.syncFromServer()
}catch(e){
  window.alert("cant get settings from server :(")
}
</script>

<template>
<h1>This is the main page</h1>

  <button @click="run_debug()">The magical debug button</button>
</template>

<style scoped>

</style>