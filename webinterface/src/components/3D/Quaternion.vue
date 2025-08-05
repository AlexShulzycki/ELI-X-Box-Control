
<script setup lang="ts">
const {xyzw, writable = true} = defineProps<{ xyzw:[number, number, number, number], writable?: boolean }>()
</script>

<template>
  <div v-if="writable">
    X: <input v-model="xyzw[0]" type="number" />
    Y: <input v-model="xyzw[1]" type="number" />
    Z: <input v-model="xyzw[2]" type="number" />
    W: <input v-model="xyzw[3]" type="number" />
  </div>
  <div v-else>X: {{xyzw[0]}} Y: {{xyzw[1]}} Z: {{xyzw[2]}} W: {{xyzw[3]}}</div>
</template>

<style scoped>

</style>