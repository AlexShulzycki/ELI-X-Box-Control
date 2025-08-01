<script setup lang="ts">
import {type SchemaNode} from "json-schema-library";
import {ref} from "vue";
import {useConfigurationStore} from "@/stores/ConfigurationStore.ts";

const configstore = useConfigurationStore();

// Declare props
const {brandNew = false, serverstate = {}} = defineProps<{ serverstate?: Object, brandNew?: boolean }>();

// update state when we wait for the response from the server
interface responseinterface {
  identifier: number;
  success: boolean;
  error?: string;
}

// -1 is used as a flag here, if its -1 then don't display the message
const response = ref({identifier: -1, success: false, error: ""} as responseinterface);

// Variables for updating configuration
const identifier = ref(serverstate.identifier)
const model = ref(serverstate.model)
const type = ref(serverstate.kind)
const min = ref(serverstate.minimum)
const max = ref(serverstate.maximum)

function updateToServer() {

  const config = {
    "Virtual":
        [{
          "identifier": identifier.value,
          "model": model.value,
          "type": type.value,
          "minimum": min.value,
          "maximum": max.value,
        }]
  }
  console.log(config)
  configstore.pushConfig(config).then((res) => {
    if (res != undefined) {
      response.value = res[0] as responseinterface;

      // set the flag back to -1 to hide the message, vary the timeouts if successful/unsuccessful
      if (response.value.success) {
        setTimeout(() => {
          response.value.identifier = -1
        }, 3000)
        // also resync the server settings
        configstore.syncServerConfigState()
      } else {
        //setTimeout(()=>{response.value.identifier = -1}, 10000)
      }
    }
  })
}

</script>

<template>
  <div v-if="response.identifier != -1">
    <h4 v-if="response.success">Successfully updated</h4>
    <h4 v-if="!response.success">Error: {{ response.error }}</h4>
  </div>

  <table v-if="!brandNew">
    <tbody>
    <tr>
      <th>Field</th>
      <th>Server State</th>
      <th>Update configuration</th>
    </tr>
    <tr>
      <th>Identifier</th>
      <td>{{ serverstate.identifier }}</td>
      <td>
        <button @click="configstore.removeConfig('Virtual', serverstate.identifier)">Remove Stage</button>
      </td>
    </tr>
    <tr>
      <th>Model</th>
      <td>{{ serverstate.model }}</td>
      <td><input v-model="model"/></td>
    </tr>
    <tr>
      <th>Stage Type</th>
      <td>{{ serverstate.kind }}</td>
      <td>
        <select v-model="type">
          <option disabled value="">Please select one</option>
          <option>linear</option>
          <option>rotational</option>
        </select></td>
    </tr>
    <tr>
      <th>Min/Max</th>
      <td>{{ serverstate.minimum }} - {{ serverstate.maximum }}mm</td>
      <td>Min: <input v-model="min"> Max: <input v-model="max"/>
      </td>
    </tr>
    </tbody>
  </table>

  <table v-else-if="brandNew">
    <tbody>
    <tr>
      <th>Identifier</th>
      <td><input v-model="identifier"/></td>
    </tr>
    <tr>
      <th>Model</th>
      <td><input v-model="model"/></td>
    </tr>
    <tr>
      <th>Type of stage</th>
      <td>
        <select v-model="type">
          <option disabled value="">Please select one</option>
          <option>linear</option>
          <option>rotational</option>
        </select></td>
    </tr>
    <tr>
      <th>Min/Max</th>
      <td>Min: <input v-model="min"> Max: <input v-model="max"/></td>
    </tr>
    </tbody>
  </table>

  <button @click="updateToServer()">Sent to server for update</button>

</template>

<style scoped>

</style>