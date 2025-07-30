<script setup lang="ts">
import {useConfigurationStore} from "@/stores/ConfigurationState.ts";
import {ref} from "vue";

const config = useConfigurationStore();



</script>

<template>
<div v-for="state in config.serverConfigs.get('PI')" :key="state.SN">

</div>
</template>

<style scoped>

</style>