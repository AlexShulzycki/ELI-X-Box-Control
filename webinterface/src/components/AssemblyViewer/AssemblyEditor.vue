<script setup lang="ts">

import {useAssemblyStore, ComponentType} from "@/stores/AssemblyStore.ts";
import ChildViewer from "@/components/AssemblyViewer/ChildViewer.vue";
import {ref, watch} from "vue";
import type {WindowGrid} from "@/stores/LayoutStore.ts";

const astore = useAssemblyStore()
astore.syncServerAssembly()

const {root = "root"} = defineProps<{ root?: string }>();

const rootnode = ref(root)
const emit = defineEmits(['changetree'])

watch(rootnode, () => {
  emit("changetree", {root: rootnode.value})
})

const selectedAssembly = ref("")
const saveAsName = ref("default")

function saveAssemblyAs() {
  if (astore.serverSavedAssemblies.get(saveAsName.value) != null) {
    if (!window.confirm("Subassembly under name " + saveAsName.value + " exists, overwrite?")) {
      return
    }
  }
  astore.saveCurrentAssembly(saveAsName.value)
}

</script>

<template>
  <button v-if="astore.hasUnsavedEdits" @click="astore.submitEditAssembly()">Submit Edits</button>
  <button @click="astore.fetchSavedSeverAssemblies()">(re)fetch saved presets from server</button>
  <button @click="saveAssemblyAs()">Save current assembly under name: </button> <input v-model="saveAsName"/>
  <div>
    Load saved preset:
    <select v-model="selectedAssembly">
      <option v-for="([name, comp], index) in astore.serverSavedAssemblies">{{ name }}</option>
    </select>
    <button v-if="astore.serverSavedAssemblies.get(selectedAssembly) != undefined" @click="astore.overWriteEditAssembly(astore.serverSavedAssemblies.get(selectedAssembly))">Load</button>
  </div>
  <h2>Root</h2>
  <ChildViewer v-bind:this_comp_name="rootnode"/>

</template>

<style scoped>

</style>