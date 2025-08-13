<script setup lang="ts">
import {type responseinterface, useConfigurationStore} from "@/stores/ConfigurationStore.ts";
import {ref} from "vue";

const configstore = useConfigurationStore()
const emit = defineEmits(['success'])
const {brandNew = false, serverstate = {min_max: [0, 0]}} = defineProps<{ serverstate?: Object, brandNew?: boolean }>();

// -1 is used as a flag here, if its -1 then don't display the message
const response = ref({identifier: -1, success: false, error: ""} as responseinterface);
const SN = ref<number>(serverstate.SN)
const model = ref<string>(serverstate.model)
const min_max = ref(serverstate.min_max)
const homed = ref<boolean>(serverstate.homed)

function updateToServer() {

  const config = {
    "Standa":
        [{
          "SN": SN.value,
          "model": model.value,
          "min_max": min_max.value,
          "connected": true,
          "homed": homed.value,
        }]
  }
  console.log("Sent config to server: ", config)
  configstore.pushConfig(config).then((res) => {
    if (res != undefined) {
      response.value = res[0] as responseinterface;

      // set the flag back to -1 to hide the message, vary the timeouts if successful/unsuccessful
      if (response.value.success) {
        // emit a success
        emit("success")
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
  <table>
    <tbody>
    <tr>
      <th>Field</th>
      <th>Update to</th>
      <th v-if="brandNew">Server Configuration</th>
    </tr>
    <tr>
      <th>Serial Number</th>
      <td v-if="brandNew">
        <select v-model="SN">
          <!--Grabbing the available device SN's (i.e. detected by the server) from the schema-->
          <option v-for="dev in configstore.getSchemaNodes.get('Standa').properties.SN.schema.anyOf" :value="dev.const">
            {{dev.const}} ({{dev.title}})
          </option>
        </select>
      </td>
      <td v-else>
        <p>{{serverstate.SN}}</p>
      </td>
    </tr>
    <tr>
      <th>Stage Model</th>
      <td v-if="brandNew">
        <select v-model="model">
          <option v-for="m in configstore.getSchemaNodes.get('Standa').properties.model.schema.enum" :value="m">
            {{m}}
          </option>
        </select>
      </td>
      <td v-if="serverstate.model != undefined">
        {{serverstate.model}}
      </td>
    </tr>
    <tr>
      <th>Connected</th>
      <td v-if="brandNew"></td>
      <td v-else>{{serverstate.connected}}</td>
    </tr>
    <tr>
      <th>Homed</th>
      <td><input v-model="homed" type="checkbox"/></td>
      <td v-if="!brandNew">{{serverstate.homed}}</td>
    </tr>
    </tbody>
  </table>
<button @click="response = {identifier:-1, success: true}; updateToServer()">Update to server</button>
<button v-if="!brandNew" @click="configstore.removeConfig('Standa', serverstate.SN); configstore.syncServerConfigState()">Remove from server</button>
</template>

<style scoped>

</style>