<script setup lang="ts">

import SchemaForm from "@/components/ConfigComponents/SchemaForm.vue";
import type {SchemaNode} from "json-schema-library";
import {ref} from "vue";
import type {Configuration} from "@/stores/ConfigurationStore.ts";


const {schema, data} = defineProps<{
  schema: SchemaNode,
  data: Configuration[]
}>();


function added_new(SN: number) {
  tab.value = SN
  newData.value = {SN: null}
}

const tab = ref<null|number>(null)

const newData = ref({SN: null})

</script>

<template>

  <v-tabs v-model="tab">
    <v-tab v-for="state in data" :value="state.SN">{{ state.SN }}</v-tab>
    <v-tab value="new"><v-icon icon="mdi-plus"/></v-tab>
  </v-tabs>
  <v-tabs-window v-model="tab">
    <v-tabs-window-item v-for="state in data" :value="state.SN">
      <SchemaForm v-bind:schemanode="schema" v-bind:serverdata="state"/>
    </v-tabs-window-item>
    <v-tabs-window-item value="new">
      <SchemaForm v-bind:serverdata="newData" v-bind:schemanode="schema" @success="added_new($event)"/>
    </v-tabs-window-item>
  </v-tabs-window>
</template>


<style>
@import '@jsonforms/vue-vuetify/lib/jsonforms-vue-vuetify.css';
</style>