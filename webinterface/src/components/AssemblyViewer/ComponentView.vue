<script setup lang="ts">
import {type Component, ComponentType, useAssemblyStore} from "@/stores/AssemblyStore.ts"
import {ref} from "vue";
import ChildViewer from "@/components/AssemblyViewer/ChildViewer.vue";
import XYZCoordinate from "@/components/3D/XYZCoordinate.vue";

const astore = useAssemblyStore()

const {servercomponent, editcomponent} = defineProps<{
  servercomponent?: Component,
  editcomponent: Component
}>();

</script>

<template>
  <table>
    <tbody>
    <tr>
      <th>Name</th>
      <td v-if="servercomponent != undefined">{{ servercomponent.name }}</td>
      <td v-else><input v-model="editcomponent.name"/></td>
    </tr>
    <tr>
      <th>Attachment Point</th>
      <td v-if="servercomponent != undefined"><XYZCoordinate v-bind:xyz="servercomponent.attachment_point" v-bind:writable="false"/></td>
      <td><XYZCoordinate v-bind:xyz="editcomponent.attachment_point"/></td>
    </tr>
    <tr>
      <th>Rotation</th>
      <td v-if="servercomponent != undefined"><XYZCoordinate v-bind:xyz="servercomponent.attachment_rotation" v-bind:writable="false"/></td>
      <td><XYZCoordinate v-bind:xyz="editcomponent.attachment_rotation"/></td>
    </tr>
    </tbody>
  </table>
  <h2>Children:</h2>
    <ChildViewer v-bind:this_comp_name="editcomponent.name"/>
</template>

<style scoped>

</style>