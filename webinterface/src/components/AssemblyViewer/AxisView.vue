<script setup lang="ts">
import type {Axis, Structure} from "@/stores/AssemblyStore.ts";
import {ref} from "vue";

const {axis} = defineProps<{ axis: Axis }>()

const structure = ref<Structure>({
  name: axis.name,
  type: axis.type,
  attach_to: axis.attach_to,
  attachment_point: axis.attachment_point,
  attachment_rotation: axis.attachment_rotation,
  collision_box_point: axis.collision_box_point,
  collision_box_dimensions: axis.collision_box_dimensions,
  children: axis.children
} as Structure)
</script>

<template>
  <p>Axis ID: {{axis.axis_identifier}}</p>
  <p>Axis Vector: {{axis.axis_vector}}</p>
  <Structure v-bind:structure="structure"/>
</template>

<style scoped>

</style>