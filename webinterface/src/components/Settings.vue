<script setup lang="ts">
import VirtualConfigBrowser from "@/components/ConfigComponents/Virtual/VirtualConfigBrowser.vue";
import PIConfigBrowser from "@/components/ConfigComponents/PI/PIConfigBrowser.vue";
import {useConfigurationStore} from "@/stores/ConfigurationStore.ts";
import {ref} from "vue";
import {useStageStore} from "@/stores/StageStore.ts";
import StandaConfigBrowser from "@/components/ConfigComponents/Standa/StandaConfigBrowser.vue";

const config = useConfigurationStore()
const StageInterface = useStageStore()

const hidden = ref(false)

function refresh() {
  config.syncConfigSchema()
  config.syncServerConfigState()
}
</script>
<!--https://www.w3schools.com/howto/howto_js_sidenav.asp Do the sidebar properly-->
<template>
      <h1>Beautiful settings tab (in progress)</h1>
      <button @click="refresh()">Server Refresh</button>
      <button @click="StageInterface.fullRefresh()">Sync stage status from server</button>
      <button @click="config.loadConfigSet('default')">Load defaults</button>
      <button @click="config.saveCurrentConfigSet('default')">Save current config as default</button>
      <div v-for="key in config.configSchemas.keys()">
        <VirtualConfigBrowser v-if="key == 'Virtual'"/>
        <PIConfigBrowser v-else-if="key == 'PI'"/>
        <StandaConfigBrowser v-else-if="key == 'Standa'"/>
        <h4 v-else>Schema {{ key }} does not have a settings page implemented yet.</h4>
      </div>
</template>

<style scoped>
template {
  height: 100%;
}

</style>