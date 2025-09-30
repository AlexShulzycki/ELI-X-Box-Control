<script setup lang="ts">
import { JsonForms, type JsonFormsChangeEvent } from "@jsonforms/vue";
import { defaultStyles, mergeStyles, vanillaRenderers } from "@jsonforms/vue-vanilla";

const renderers = Object.freeze([
  ...vanillaRenderers,
  // here you can add custom renderers
]);

import type {SchemaNode} from "json-schema-library";

const {schemanode} = defineProps<{
  schemanode: SchemaNode,
}>();

</script>

<template>

  <h1>JSON Forms Vue 3</h1>
  <div class="myform">
    <json-forms :renderers="renderers" :schema="schemanode.schema" />
  </div>
</template>


<style scoped>

</style>