<script setup lang="ts">
import type {Structure} from "@/stores/AssemblyStore.ts";
import ComponentView from "@/components/AssemblyViewer/ComponentView.vue";
import XYZCoordinate from "@/components/3D/XYZCoordinate.vue";

const {serverstructure, editstructure} = defineProps<{
  serverstructure?: Structure,
  editstructure: Structure
}>();

</script>

<template>
  <table>
    <tbody>
    <tr>
      <th>Collision Box Dimensions</th>
      <th>Collision Box Center</th>
    </tr>
    <tr v-if="serverstructure != null">
      <td><XYZCoordinate v-bind:xyz="serverstructure.collision_box_dimensions" v-bind:writable="false"/></td>
      <td><XYZCoordinate v-bind:xyz="serverstructure.collision_box_point" v-bind:writable="false"/></td>
    </tr>
    <tr>
      <td><XYZCoordinate v-bind:xyz="editstructure.collision_box_dimensions"/></td>
      <td><XYZCoordinate v-bind:xyz="editstructure.collision_box_point"/></td>
    </tr>
    </tbody>
  </table>
  <ComponentView v-bind:servercomponent="serverstructure" v-bind:editcomponent="editstructure"/>
</template>

<style scoped>

</style>