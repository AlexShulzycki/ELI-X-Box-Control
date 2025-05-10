<script setup lang="ts">

import {C884Axis, C884Controller} from "@/stores/AxisState.ts";

defineProps({controller: {
  type: C884Controller,
  required: true}
})

</script>

<template>
  <h1>COM port: {{controller.comport}}</h1>
  <h1> Baud rate: {{controller.baudrate}}</h1>
</template>

<style scoped>

</style>