<script setup lang="ts">
import {useConfigurationStore} from "@/stores/ConfigurationStore.ts";
import {ref} from "vue";
import {useStageStore} from "@/stores/StageStore.ts";
import SchemaFormBrowser from "@/components/ConfigComponents/SchemaFormBrowser.vue";

const config = useConfigurationStore()
const StageInterface = useStageStore()

const hidden = ref(false)

function refresh() {
  config.syncConfigSchema()
  config.syncServerConfigState()
}
</script>

<template>
  <v-btn-group>
    <v-btn @click="refresh()">Server Refresh</v-btn>
    <v-btn @click="StageInterface.fullRefresh()">Sync stage status from server</v-btn>
    <v-btn @click="config.loadConfigSet('default')">Load defaults</v-btn>
    <v-btn @click="config.saveCurrentConfigSet('default')">Save current config as default</v-btn>
  </v-btn-group>
  <div v-for="[key, [schema, data]] in config.getConfigWithSchema">
    <SchemaFormBrowser v-bind:schema="schema" v-bind:data="data"/>
  </div>

</template>

<style scoped>
template {
  height: 100%;
}

</style>