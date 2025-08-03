<script setup lang="ts">
import {type Component, type Structure, ComponentType, type Axis} from "@/stores/AssemblyStore.ts";
import StructureView from "@/components/AssemblyViewer/StructureView.vue";
import ComponentView from "@/components/AssemblyViewer/ComponentView.vue";
import AxisView from "@/components/AssemblyViewer/AxisView.vue";

const {child} = defineProps<{ child: Object }>()

if(child.type == undefined){
  console.log("Invalid child component, cannot view", child)
}
</script>

<template>
  <ComponentView v-if="child.type == ComponentType.Component" v-bind:component="child as Component"/>
  <StructureView v-else-if="child.type == ComponentType.Structure" v-bind:structure="child as Structure"/>
  <AxisView v-else-if="child.type == ComponentType.Axis" v-bind:axis="child as Axis"/>
</template>

<style scoped>

</style>