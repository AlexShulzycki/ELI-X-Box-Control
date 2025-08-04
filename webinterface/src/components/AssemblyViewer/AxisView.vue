<script setup lang="ts">
import type {Axis} from "@/stores/AssemblyStore.ts";
import StructureView from "@/components/AssemblyViewer/StructureView.vue";
import XYZCoordinate from "@/components/3D/XYZCoordinate.vue";

const {serveraxis, editaxis} = defineProps<{ serveraxis?: Axis, editaxis: Axis }>()

</script>

<template>
  <table>
    <tbody>
    <tr>
      <th>Axis Identifier</th>
      <th>Axis Vector</th>
    </tr>
    <tr v-if="serveraxis != null">
      <td>{{ serveraxis.axis_identifier }}</td>
      <td><XYZCoordinate v-bind:xyz="serveraxis.axis_vector" v-bind:writable="false"/></td>
    </tr>
    <tr>
      <td><input v-model="editaxis.axis_identifier"/></td>
      <td><XYZCoordinate v-bind:xyz="editaxis.axis_vector"/></td>
    </tr>
    </tbody>
  </table>
  <StructureView v-bind:serverstructure="serveraxis" v-bind:editstructure="editaxis"/>
</template>

<style scoped>

</style>