<script setup lang="ts">

import {useAssemblyStore, ComponentType} from "@/stores/AssemblyStore.ts";
import type {Component, Structure, Axis} from "@/stores/AssemblyStore.ts"
import ChildViewer from "@/components/AssemblyViewer/ChildViewer.vue";
const astore = useAssemblyStore()

astore.syncServerAssembly()

</script>

<template>

  <h2>Root</h2>
  <ChildViewer this_comp_name="root" />

</template>

<style scoped>

</style>