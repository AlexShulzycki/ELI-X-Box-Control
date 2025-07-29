<script setup lang="ts">
import {type SchemaNode} from "json-schema-library";
import {ref} from "vue";
import axios from "axios";
import {useConfigurationStore} from "@/stores/ConfigurationState.ts";

const configstore = useConfigurationStore();

// Declare props
interface Props {
  schema: SchemaNode | undefined,
  state: Object
}
const props = defineProps<Props>()

// Variables for updating configuration
const model = ref(props.state.model)
const type = ref(props.state.kind)
const min = ref(props.state.minimum)
const max = ref(props.state.maximum)

</script>

<template>
  <table>
    <tr>
      <th>Identifier</th>
      <th>Update configuration</th>
    </tr>
    <tr>
      <td>{{props.state.identifier}}</td>
      <td><button @click="configstore.removeConfig('Virtual', props.state.identifier)">Remove Stage</button></td>
    </tr>
    <tr>
      <td>Model: {{props.state.model}}</td>
      <td><input v-model="model"/></td>
    </tr>
    <tr>
      <td>Type of stage: {{props.state.kind}}</td>
      <td>
        <select v-model="type">
          <option disabled value="">Please select one</option>
          <option>linear</option>
          <option>rotational</option>
        </select></td>
    </tr>
    <tr>
      <td>Min/Max: {{props.state.minimum}} - {{props.state.maximum}}mm</td>
      <td>Min: <input v-model="min"> Max: <input v-model="max"/>
      </td>
    </tr>
  </table>

</template>

<style scoped>

</style>