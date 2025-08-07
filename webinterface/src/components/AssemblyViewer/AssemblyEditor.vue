<script setup lang="ts">

import {useAssemblyStore, ComponentType} from "@/stores/AssemblyStore.ts";
import ChildViewer from "@/components/AssemblyViewer/ChildViewer.vue";
import {ref, watch} from "vue";
import type {WindowGrid} from "@/stores/LayoutStore.ts";

const astore = useAssemblyStore()
astore.syncServerAssembly()

const {root = "root"} = defineProps<{ root?:string }>();

const rootnode = ref(root)
const emit = defineEmits(['changetree'])

watch(rootnode, ()=>{
  emit("changetree", {root: rootnode.value})
})

</script>

<template>
  <button v-if="astore.hasUnsavedEdits" @click="astore.submitEditAssembly()">Submit Edits</button>
  <h2>Root</h2>
  <ChildViewer v-bind:this_comp_name="rootnode" />

</template>

<style scoped>

</style>