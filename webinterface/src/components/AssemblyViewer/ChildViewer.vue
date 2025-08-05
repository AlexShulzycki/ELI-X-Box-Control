<script setup lang="ts" xmlns="http://www.w3.org/1999/html">
import {type Component, type Structure, ComponentType, type Axis, useAssemblyStore} from "@/stores/AssemblyStore.ts";
import StructureView from "@/components/AssemblyViewer/StructureView.vue";
import ComponentView from "@/components/AssemblyViewer/ComponentView.vue";
import AxisView from "@/components/AssemblyViewer/AxisView.vue";
import {ref} from "vue";

const astore = useAssemblyStore()

const {this_comp_name} = defineProps<{
  this_comp_name: string
}>()

if (astore.serverAssembly == null) {
  console.error("serverAssembly not initialized yet")
}

let addNewType = ref<ComponentType>(ComponentType.Component)
let addNewName = ref("Unique Name Here")

function addAnother() {
  // Append a new child component
  let data: any = {
    name: addNewName.value,
    type: addNewType.value,
    attach_to: this_comp_name,
    attachment_point: [0, 0, 0],
    attachment_rotation: [0, 0, 0, 1],
    children: [],
  }

  // populate default values for different types
  if (addNewType.value == ComponentType.Component) {
    astore.addChild(this_comp_name, data as Component)
  } else if (addNewType.value == ComponentType.Structure) {
    data.collision_box_dimensions = [0, 0, 0]
    data.collision_box_point = [0, 0, 0]
    astore.addChild(this_comp_name, data as Structure)
  } else if (addNewType.value == ComponentType.Axis) {
    data.axis_identifier = 0
    data.axis_vector = [1, 0, 0]
    astore.addChild(this_comp_name, data as Axis)
  } else {
    console.error("Error adding axis", addNewType.value, "unknown type")
  }
}

</script>

<template>
  <div class="container">
    <div v-for="editchild in astore.getEditMap?.get(this_comp_name)?.children" :key="editchild.name">
      <ComponentView v-if="editchild.type == ComponentType.Component"
                     v-bind:servercomponent="astore.getServerMap?.get(editchild.name) as Component"
                     v-bind:editcomponent="editchild as Component"/>
      <StructureView v-else-if="editchild.type == ComponentType.Structure"
                     v-bind:serverstructure="astore.getServerMap?.get(editchild.name) as Structure"
                     v-bind:editstructure="editchild as Structure"/>
      <AxisView v-else-if="editchild.type == ComponentType.Axis"
                v-bind:serveraxis="astore.getServerMap?.get(editchild.name) as Axis"
                v-bind:editaxis="editchild as Axis"/>
    </div>
    <br/>
    <select v-model="addNewType">
      <option v-for="comp in ComponentType">{{ comp }}</option>
    </select>
    <input v-model="addNewName"/>
    <button @click="addAnother()">Add another</button>
  </div>
</template>

<style scoped>
.container {
  padding: 2vw;
  border-radius: 5px;
  border: medium solid black;
}
</style>