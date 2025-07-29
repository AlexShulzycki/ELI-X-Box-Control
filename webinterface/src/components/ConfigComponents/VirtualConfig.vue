<script setup lang="ts">
import {type SchemaNode} from "json-schema-library";

// Declare props
interface Props {
  schema: SchemaNode | undefined,
  state: Object
}
const props = defineProps<Props>()

</script>

<template>
  <table>
    <tr>
      <th>Identifier: {{props.state.identifier}}</th>
      <th>Update configuration:</th>
    </tr>
    <tr>
      <td>Model: {{props.state.model}}</td>
    </tr>
    <tr>
      <td>Type of stage: {{props.state.kind}}</td>
    </tr>
    <tr>
      <td>Min/Max: {{props.state.minimum}} - {{props.state.maximum}}mm</td>
    </tr>
  </table>

</template>

<style scoped>

</style>