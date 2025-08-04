<script setup lang="ts">
const {xyz, writable = true} = defineProps<{ xyz:[number, number, number], writable?: boolean }>()
</script>

<template>
  <div v-if="writable">
    X: <input v-model="xyz[0]" type="number" />
    Y: <input v-model="xyz[1]" type="number" />
    Z: <input v-model="xyz[2]" type="number" />
  </div>
  <div v-else>X: {{xyz[0]}} Y: {{xyz[1]}} Z: {{xyz[2]}}</div>
</template>

<style scoped>

</style>