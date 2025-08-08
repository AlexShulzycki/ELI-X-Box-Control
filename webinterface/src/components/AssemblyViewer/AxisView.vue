<script setup lang="ts">
import type {Axis} from "@/stores/AssemblyStore.ts";
import StructureView from "@/components/AssemblyViewer/StructureView.vue";
import XYZCoordinate from "@/components/3D/XYZCoordinate.vue";
import Quaternion from "@/components/3D/Quaternion.vue";

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
      <td v-if="serveraxis.axis_vector != null">
        <XYZCoordinate v-if="serveraxis.axis_vector.length == 3" v-bind:xyz="serveraxis.axis_vector"
                       v-bind:writable="false"/>
        <Quaternion v-else-if="serveraxis.axis_vector.length == 4" v-bind:xyzw="serveraxis.axis_vector"
                    v-bind:writable="false"/>
      </td>
    </tr>
    <tr>
      <td><input v-model="editaxis.axis_identifier"/></td>
      <!--TODO Give option to switch between linear and rotational axes-->
      <td v-if="editaxis.axis_vector != null">
        <XYZCoordinate v-if="editaxis.axis_vector.length == 3" v-bind:xyz="editaxis.axis_vector"
                       v-bind:writable="false"/>
        <Quaternion v-else-if="editaxis.axis_vector.length == 4" v-bind:xyzw="editaxis.axis_vector"
                    v-bind:writable="false"/>
      </td>
    </tr>
    </tbody>
  </table>
  <StructureView v-bind:serverstructure="serveraxis" v-bind:editstructure="editaxis"/>
</template>

<style scoped>

</style>