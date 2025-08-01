<script setup lang="ts">
import {useConfigurationStore} from "@/stores/ConfigurationStore.ts";
import {ref} from "vue";
import PIConfigViewer from "@/components/ConfigComponents/PI/PIConfigViewer.vue";

const config = useConfigurationStore();

let hidden = ref(true)

function toggleHidden() {
  hidden.value = !hidden.value;
}


</script>

<template>
  <h1>Configurations for PI Controllers</h1>
  <PIConfigViewer
      v-for="state in config.serverConfigs.get('PI')"
      :key="state.SN"
      v-bind:serverstate="state"
  />

  <button @click="toggleHidden()" v-if="hidden">Add another configuration</button>
  <div v-else>
    <button @click="toggleHidden()">Close new config edit</button>
    <PIConfigViewer v-bind:brand-new="true"/>
  </div>


</template>

<style scoped>

</style>