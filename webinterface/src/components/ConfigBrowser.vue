<script setup lang="ts">
import {useConfigurationStore} from "@/stores/ConfigurationState.ts";
import VirtualConfig from "@/components/ConfigComponents/VirtualConfig.vue";
const config = useConfigurationStore();

// Declare props
interface Props {
  config_type_key: string;
}
const props = defineProps<Props>()

</script>

<template>
<div class="flex-container">
  <h1>Configuration Browser for {{props.config_type_key}}</h1>
    <virtual-config
        v-if="props.config_type_key == 'Virtual'"
        v-for="state in config.serverConfigs.get(props.config_type_key)"
        v-bind:schema="config.configSchemas.get(config_type_key)"
        v-bind:state="state"
    />
  <h4 v-else>Schema {{config_type_key}} does not have a settings page implemented yet.</h4>
</div>
</template>

<style scoped>
.flex-container {
  display: flex;
  flex-direction: column;
}
</style>