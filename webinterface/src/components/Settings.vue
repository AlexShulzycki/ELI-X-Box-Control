<script setup lang="ts">
import VirtualConfigBrowser from "@/components/ConfigComponents/Virtual/VirtualConfigBrowser.vue";
import PIConfigBrowser from "@/components/ConfigComponents/PI/PIConfigBrowser.vue";
import {useConfigurationStore} from "@/stores/ConfigurationStore.ts";
import {ref} from "vue";
import {useStageStore} from "@/stores/StageStore.ts";

const config = useConfigurationStore()
const StageInterface = useStageStore()

const hidden = ref(false)

function refresh() {
  config.syncConfigSchema()
  config.syncServerConfigState()
}
</script>

<template>
  <div class="slidecontainer">
    <div class="content" :class="{slideout: !hidden, closed: hidden}">
      <h1>Beautiful settings tab (in progress)</h1>
      <button @click="refresh()">Server Refresh</button>
      <button @click="StageInterface.fullRefresh()">Sync stage status from server</button>
      <button @click="config.loadConfigSet('default')">Load defaults</button>
      <button @click="config.saveCurrentConfigSet('default')">Save current config as default</button>
      <div v-for="key in config.configSchemas.keys()">
        <VirtualConfigBrowser v-if="key == 'Virtual'"/>
        <PIConfigBrowser v-else-if="key == 'PI'"/>
        <h4 v-else>Schema {{ key }} does not have a settings page implemented yet.</h4>
      </div>
    </div>
    <button class="slidebutton" @click="hidden = !hidden"> <</button>
  </div>
</template>

<style scoped>
template {
  height: 100%;
}

.slidecontainer {
  position: absolute;
  z-index: 1;
  right: 0;
  height: 100%;
  display: grid;
}

.content {
  padding: 0 2vw 0 2vw;
  background-color: darkgrey;
  height: 100%;
  width: 100%;
  grid-column: 2;
  grid-row: 1;
}

.slideout {
  max-width: 50vw
}

.closed {
  width: 0;
  padding: 0;
  margin: 0;
  display: none;
  grid-column:1
}

.slidebutton {
  height: 100%;
  grid-column: 1;
  grid-row: 1;
}
</style>