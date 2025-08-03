<script setup lang="ts">
import {type Component, ComponentType, type XYZ} from "@/stores/AssemblyStore.ts"
import {ref} from "vue";
import ChildViewer from "@/components/AssemblyViewer/ChildViewer.vue";

const {comp: component} = defineProps<{ component: Component }>()

let name = ref<string>(component.name)
let type = ref<ComponentType>(component.type)
let attach_to = ref<string>(component.attach_to)
let attachment_point = ref<XYZ>({x: 0, y: 0, z: 0})
let attachment_rotation = ref<XYZ>({x: 0, y: 0, z: 0})
let children = ref<Component[]>(component.children)

</script>

<template>
  <table>
    <tbody>
    <tr>
      <th>Name</th>
      <td>{{ name }}</td>
    </tr>
    <tr>
      <th>Type</th>
      <td>{{type}}</td>
    </tr>
    <tr>
      <th>Attached at</th>
      <td>{{attachment_point}}</td>
    </tr>
    <tr>
      <th>Rotation</th>
      <td>{{attachment_rotation}}</td>
    </tr>
    </tbody>
  </table>
  <h2>Children:</h2>
  <div v-for="child in component.children" :key="child.name">
      <ChildViewer v-bind:child="child"/>
  </div>
</template>

<style scoped>

</style>