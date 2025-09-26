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



const schema = {
  properties: {
    name: {
      type: "string",
      minLength: 1,
      description: "The task's name"
    },
    description: {
      title: "Long Description",
      type: "string",
    },
    done: {
      type: "boolean",
    },
    dueDate: {
      type: "string",
      format: "date",
      description: "The task's due date"
    },
    rating: {
      type: "integer",
      maximum: 5,
    },
    recurrence: {
      type: "string",
      enum: ["Never", "Daily", "Weekly", "Monthly"]
    },
    recurrenceInterval: {
      type: "integer",
      description: "Days until recurrence"
    },
  },
};

</script>

<template>

  <h1>JSON Forms Vue 3</h1>
  <div class="myform">
    <json-forms :renderers="renderers" :schema="schemanode.schema" />
  </div>
</template>


<style scoped>

</style>