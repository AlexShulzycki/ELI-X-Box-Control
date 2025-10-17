<script setup lang="ts">

import SchemaForm from "@/components/ConfigComponents/SchemaForm.vue";
import type {SchemaNode} from "json-schema-library";
import {ref} from "vue";
import type {Configuration} from "@/stores/ConfigurationStore.ts";


const {schema, data} = defineProps<{
  schema: SchemaNode,
  data: Configuration[]
}>();

let hidden = ref(true)

function toggleHidden() {
  hidden.value = !hidden.value;
}

const tab = ref(null)

</script>

<template>

  <v-btn @click="toggleHidden()" v-if="hidden">Add another configuration</v-btn>
  <div v-else>
    <v-btn @click="toggleHidden()">Close new config edit</v-btn>
    <SchemaForm v-bind:schemanode="schema" @success="toggleHidden"/>
  </div>
  <v-tabs v-model="tab">
    <v-tab v-for="state in data">{{ state.SN }}</v-tab>
  </v-tabs>
  <v-tabs-window v-model="tab">
    <v-tabs-window-item v-for="state in data">
      <SchemaForm v-bind:schemanode="schema" v-bind:serverdata="state"/>
    </v-tabs-window-item>
  </v-tabs-window>
</template>


<style>
@import '@jsonforms/vue-vuetify/lib/jsonforms-vue-vuetify.css';
</style>