<script setup lang="ts">

import {readonly, ref, watch} from "vue";
import {useConfigurationStore, type responseinterface} from "@/stores/ConfigurationStore.ts";

const configstore = useConfigurationStore();

const {
  brandNew = false, serverstate = {
    // initialize variables if empty
    stages: [], clo: [], referenced: [], min_max: []
  }
} = defineProps<{ serverstate?: Object, brandNew?: boolean }>();

// -1 is used as a flag here, if its -1 then don't display the message
const response = ref({identifier: -1, success: false, error: ""} as responseinterface);

// variables for editing configuration. We have to force a deep copy, because we don't want to ref a reference, we just
// want to set default values. Apparently double JSONing it is a highly rated stackoverflow answer. I hate typescript.
const SN = ref<number>(JSON.parse(JSON.stringify(serverstate.SN)))
const model = ref<string>(JSON.parse(JSON.stringify(serverstate.model)))
const connection_type = ref<string>(JSON.parse(JSON.stringify(serverstate.connection_type)))
const channel_amount = ref<number>(JSON.parse(JSON.stringify(serverstate.channel_amount)))
const stages = ref<Array<string>>(JSON.parse(JSON.stringify(serverstate.stages)));
const clo = ref<Array<boolean>>(JSON.parse(JSON.stringify(serverstate.clo)));
const referenced = ref<Array<boolean>>(JSON.parse(JSON.stringify(serverstate.referenced)))
const min_max = ref<Array<Array<number>>>(JSON.parse(JSON.stringify(serverstate.min_max)))
const baud_rate = ref<number>(JSON.parse(JSON.stringify(serverstate.baud_rate)))
const comport = ref<number>(JSON.parse(JSON.stringify(serverstate.comport)))

// Force channel_amount to dictate length of stages, clo, referenced, min_max
watch(channel_amount, (current, previous) => {
      console.log("changed channel amount", channel_amount.value)
      let difference = null
      if (previous == null) {
        difference = current
      } else {
        difference = current - previous;
      }


      if (difference > 0) {
        // we added more channels
        for (let i = 0; i < difference; i++) {
          stages.value.push("NOSTAGE")
          clo.value.push(false)
          referenced.value.push(false)
          min_max.value.push([0, 0])
        }
      } else if (difference < 0) {
        for (let i = 0; i < (difference * -1); i++) {
          stages.value.pop()
          clo.value.pop()
          referenced.value.pop()
          min_max.value.pop()
        }
      }
    }
)

function updateToServer() {

  const config = {
    "PI":
        [{
          "SN": SN.value,
          "model": model.value,
          "connection_type": connection_type.value,
          "connected": true,
          "channel_amount": channel_amount.value,
          "stages": stages.value,
          "clo": clo.value,
          "referenced": referenced.value,
          "min_max": min_max.value,
          "baud_rate": baud_rate.value,
          "comport": comport.value
        }]
  }
  console.log("Sent config to server: ", config)
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

  <table>
    <tbody>
    <tr>
      <th>Field</th>
      <th v-if="!brandNew">Server Configuration</th>
      <th>Update to</th>
    </tr>
    <tr>
      <th>Serial Number</th>
      <td v-if="brandNew"><input v-model="SN"/></td>
      <td v-else>{{ serverstate.SN }}</td>
    </tr>
    <tr>
      <th>Model</th>
      <td v-if="brandNew">
        <select v-model="model">
          <option disabled value="">Please select one</option>
          <option>C884</option>
          <!-For now only C884-/>
        </select>
      </td>
      <td v-else>{{ serverstate.model }}</td>
    </tr>
    <tr v-if="!brandNew">
      <!--TODO work on the exact interface for readonly states-->
      <th>Connection state</th>
      <td>Connected: {{ serverstate.connected }}, Ready: {{serverstate.ready}}</td>
    </tr>
    <tr>
      <th>Connection Type</th>
      <td v-if="brandNew">
        <select v-model="connection_type">
          <option disabled value="">Please select one</option>
          <option value="usb">USB</option>
          <option value="rs232">RS-232</option>
        </select>
      </td>
      <td v-else>
        <p>{{ serverstate.connection_type }}</p>
      </td>
    </tr>
    <tr v-if="connection_type == 'rs232'">
      <th>RS-232 Options</th>
      <td v-if="brandNew">
        Comport <input v-model="comport">
        Baud Rate <input v-model="baud_rate">
      </td>
      <td v-else>
        Comport {{ serverstate.comport }}
        Baud Rate {{ serverstate.baud_rate }}
      </td>
    </tr>
    <tr>
      <th>Channel Amount</th>
      <td v-if="brandNew"><input v-model="channel_amount"/></td>
      <td v-else>{{ serverstate.channel_amount }}</td>
    </tr>
    <tr>
      <th colspan="3">
        <table>
          <tbody>
          <tr>
            <th>Channel</th>
            <th v-for="(stage, index) in stages">{{ index + 1 }}</th>
          </tr>
          <tr>
            <th>Stages</th>

            <td v-for="(stage, index) in serverstate.stages" key="index">
              <p>{{ stage }}</p>
              <p>Change to:</p>
              <input v-model="stages[index]"/>
            </td>

          </tr>
          <tr>
            <th>Closed Loop Operation</th>
            <td v-for="(_clo, index) in serverstate.clo">
              <p>{{ _clo }}</p>
              <p>Change to:</p>
              <input v-model="clo[index]" type="checkbox"/>
            </td>
          </tr>
          <tr>
            <th>Referenced</th>

            <td v-for="(refd, index) in serverstate.referenced" :key="index">
              <p>{{ refd }}</p>
              <p>Change to:</p>
              <input v-model="referenced[index]" type="checkbox"/>
            </td>
          </tr>
          </tbody>
        </table>
      </th>
    </tr>
    </tbody>
  </table>

  <button @click="updateToServer()">Sent to server for update</button>
</template>

<style scoped>

</style>