<script setup lang="ts">

import {C884Controller} from "@/stores/AxisState.ts";

defineProps({controller: {
  type: C884Controller,
  required: true}
})

</script>

<template>
  <h2>COM port: {{controller.config.comport}}</h2>
  <h2>Baud rate: {{controller.config.baudrate}}</h2>
  <table>
    <tr v-for="(stage, index) in controller.stages">
      <td><b>Axis {{index + 1}}:</b></td>
      <td>Stage: {{stage.model}}</td>
      <td>Type: {{stage.type}}</td>
      <td v-if="stage.type == 'Linear'">Length: {{stage.length}}</td>
    </tr>
  </table>
</template>

<style scoped>

</style>