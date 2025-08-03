<script setup lang="ts">
import {type Component, type Structure, ComponentType, type Axis, useAssemblyStore} from "@/stores/AssemblyStore.ts";
import StructureView from "@/components/AssemblyViewer/StructureView.vue";
import ComponentView from "@/components/AssemblyViewer/ComponentView.vue";
import AxisView from "@/components/AssemblyViewer/AxisView.vue";
import {ref} from "vue";

const astore = useAssemblyStore()

const {child, parent} = defineProps<{
  child: Object,
  parent: string
}>()

if (child.type == undefined) {
  console.log("Invalid child component, cannot view", child)
}

let newtype = ref<ComponentType>(ComponentType.Component)

function addNew(name: string){
  let comp = {
    name: name,
    type: newtype,
    attach_to: child.name,
    attachment_point: child.attachment_point,
    attachment_rotation: child.attachment_rotation,
    children: []
  }
  if(comp.type.value == ComponentType.Component){
    astore.addComponent<Component>(comp)
  }
}
</script>

<template>
  <div>
    <ComponentView v-if="child.type == ComponentType.Component" v-bind:component="child as Component"/>
    <StructureView v-else-if="child.type == ComponentType.Structure" v-bind:structure="child as Structure"/>
    <AxisView v-else-if="child.type == ComponentType.Axis" v-bind:axis="child as Axis"/>
  </div>
</template>

<style scoped>

</style>