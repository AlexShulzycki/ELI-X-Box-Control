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

const tab = ref(null)
</script>

<template>
  <v-sheet width="100%">
    <v-toolbar>
      <v-btn @click="refresh()">Server Refresh</v-btn>
      <v-btn @click="config.loadConfigSet('default')">Load defaults</v-btn>
      <v-btn @click="config.saveCurrentConfigSet('default')">Save current config as default</v-btn>
    </v-toolbar>

    <v-tabs v-model="tab">
      <v-tab v-for="key in config.configSchemas.keys()" :value="key">
        {{ key }}
        <v-badge
            v-if="config.serverConfigs.get(key)?.length??0 > 0"
            color="primary"
            v-bind:content="config.serverConfigs.get(key)?.length"
            inline
        />
      </v-tab>
    </v-tabs>


    <v-tabs-window v-model="tab">
      <v-tabs-window-item v-for="[key, [schema, data]] in config.getConfigWithSchema" :value="key">
        <SchemaFormBrowser v-bind:schema="schema" v-bind:data="data"/>
      </v-tabs-window-item>
    </v-tabs-window>
  </v-sheet>
</template>

<style scoped>
template {
  height: 100%;
}

</style>