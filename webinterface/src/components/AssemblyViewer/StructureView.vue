<script setup lang="ts">

import type {Component, Structure} from "@/stores/AssemblyStore.ts";
import {ref} from "vue";

const {structure} = defineProps<{structure: Structure}>()

const comp = ref<Component>({
  name: structure.name,
  type: structure.type,
  attach_to: structure.attach_to,
  attachment_point: structure.attachment_point,
  attachment_rotation: structure.attachment_rotation,
  children: structure.children
} as Component)

</script>

<template>
  <p>Collisionbox: {{structure.collision_box_dimensions}}</p>
  <p>Collisionpoint: {{structure.collision_box_point}}</p>
<Component v-bind:comp="comp"/>
</template>

<style scoped>

</style>