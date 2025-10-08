<script setup lang="ts">

import SchemaForm from "@/components/ConfigComponents/SchemaForm.vue";
import type {SchemaNode} from "json-schema-library";
import StandaConfigViewer from "@/components/ConfigComponents/Standa/StandaConfigViewer.vue";
import {ref} from "vue";


const {schema, data} = defineProps<{
  schema: SchemaNode,
  data: object
}>();

let hidden = ref(true)

function toggleHidden() {
  hidden.value = !hidden.value;
}

</script>

<template>

  <h1>{{ schema.schema.title }}</h1>
  <v-btn @click="toggleHidden()" v-if="hidden">Add another configuration</v-btn>
  <div v-else>
    <v-btn @click="toggleHidden()">Close new config edit</v-btn>
    <SchemaForm v-bind:schemanode="schema"/>
  </div>
  <div class="myform">

  </div>
</template>


<style scoped>

</style>