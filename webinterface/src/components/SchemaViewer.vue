<script setup lang="ts">
import {useConfigurationStore} from "@/stores/ConfigurationState.ts";
import {type SchemaNode} from "json-schema-library";

// Declare props
interface Props {
  schema: SchemaNode,
  state?: Object
}
const props = defineProps<Props>()

</script>

<template>

</template>

<style scoped>

</style>