<script setup lang="ts">
import type {Structure} from "@/stores/AssemblyStore.ts";
import ComponentView from "@/components/AssemblyViewer/ComponentView.vue";

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
      <td>{{ serverstructure.collision_box_dimensions }}</td>
      <td>{{ serverstructure.collision_box_point }}</td>
    </tr>
    <tr>
      <td><input v-model="editstructure.collision_box_dimensions"/></td>
      <td><input v-model="editstructure.collision_box_point"/></td>
    </tr>
    </tbody>
  </table>
  <ComponentView v-bind:servercomponent="serverstructure" v-bind:editcomponent="editstructure"/>
</template>

<style scoped>

</style>