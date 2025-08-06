<script setup lang="ts">

import {useAssemblyStore, ComponentType} from "@/stores/AssemblyStore.ts";
import ChildViewer from "@/components/AssemblyViewer/ChildViewer.vue";
const astore = useAssemblyStore()

astore.syncServerAssembly()

</script>

<template>
  <button v-if="astore.hasUnsavedEdits" @click="astore.submitEditAssembly()">Submit Edits</button>
  <h2>Root</h2>
  <ChildViewer this_comp_name="root" />

</template>

<style scoped>

</style>