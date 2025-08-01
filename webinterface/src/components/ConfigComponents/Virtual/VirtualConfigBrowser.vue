<script setup lang="ts">
import {useConfigurationStore} from "@/stores/ConfigurationStore.ts";
import VirtualConfig from "@/components/ConfigComponents/Virtual/VirtualConfig.vue";
import {ref} from "vue";
const config = useConfigurationStore();

let hidden = ref(true)

function toggleHidden(){
  hidden.value = !hidden.value;
}

</script>

<template>
<div class="flex-container">
  <h1>Configuration Browser for Virtual Stages</h1>
    <virtual-config
        v-for="state in config.getServerConfigs.get('Virtual')"
        v-bind:serverstate="state"
        :key="state.identifier"
    />
    <button @click="toggleHidden()" v-if="hidden">Add another configuration</button>
    <div v-else>
      <button @click="toggleHidden()">Close new config edit</button>
      <virtual-config v-bind:brand-new="true"/>
    </div>


</div>
</template>

<style scoped>
.flex-container {
  display: flex;
  flex-direction: column;
}
</style>