<script setup lang="ts">
import { JsonForms} from "@jsonforms/vue";
import { extendedVuetifyRenderers } from '@jsonforms/vue-vuetify';

const renderers = Object.freeze([
  ...extendedVuetifyRenderers,
  // here you can add custom renderers
]);

import type {SchemaNode} from "json-schema-library";

const {schemanode} = defineProps<{
  schemanode: SchemaNode,
}>();

</script>

<template>

  <h1>{{ schemanode.schema.title }}</h1>
  <div class="myform">
    <json-forms :renderers="renderers" :schema="schemanode.schema" />
  </div>
</template>


<style scoped>

</style>