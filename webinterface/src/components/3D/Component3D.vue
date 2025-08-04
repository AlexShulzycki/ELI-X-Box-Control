<script setup lang="ts">
import {useTresContext} from '@tresjs/core'
import {type Component, ComponentType} from "@/stores/AssemblyStore.ts";

const {component, type} = defineProps<{
  component: Component
  type: ComponentType
}>();


const context = useTresContext()
</script>

<template>
  <TresMesh>

  </TresMesh>
</template>

<style scoped>

</style>