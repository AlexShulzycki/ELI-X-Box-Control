<script setup lang="ts">

import {ref, watch} from "vue";

const {brandNew = false, serverstate = {}} = defineProps<{ serverstate?: Object, brandNew?: boolean }>();

// variables for editing configuration
const SN = ref<number>(serverstate.SN)
const model = ref<string>(serverstate.model)
const connection_type = ref<string>(serverstate.connection_type)
const connected = ref<boolean>(serverstate.connected)
const channel_amount = ref<number>(serverstate.channel_amount)
const stages = ref<Array<string>>(serverstate.stages);
const clo = ref<Array<boolean>>(serverstate.clo);
const referenced = ref<Array<boolean>>(serverstate.referenced)
const min_max = ref<Array<Array<number>>>(serverstate.min_max)
const baud_rate = ref<number>(serverstate.baud_rate)
const comport = ref<number>(serverstate.com_port)

// Force channel_amount to dictate length of stages, clo, referenced, min_max
watch(channel_amount, (current, previous) => {
  const difference = current - previous;
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
})
</script>

<template>
  <table>
    <tr>
      <th>Field</th>
      <th>Server Configuration</th>
      <th>Update to</th>
    </tr>
    <tr>
      <th>Serial Number</th>
      <td>{{ serverstate.SN }}</td>
      <td><input v-model="SN"/></td>
    </tr>
    <tr>
      <!--TODO work on the exact interface for readonly states-->
      <th>Connected</th>
      <td>{{ serverstate.connected }}</td>
      <td><input v-model="connected" type="checkbox"/></td>
    </tr>
    <tr>
      <th>Connection Type</th>
      <td>
        <p>{{serverstate.connection_type}}</p>
        <p v-if="serverstate.connection_type == 'rs232'">Comport {{serverstate.comport}}, Baud Rate {{serverstate.baud_rate}}</p>
      </td>
    </tr>
    <tr>
      <th>Channel Amount</th>
      <td>{{serverstate.channel_amount }}</td>
      <td><input v-model="channel_amount"/></td>
    </tr>
    <tr>
      <th>Stages</th>
      <td>
        <div v-for="stage in serverstate.stages" key="index">
          <p>{{ stage }}</p>
        </div>
      </td>
      <td>
        <div v-for="stage in stages" key="index">
          <input v-model="stage"/>
        </div>
      </td>
    </tr>
    <tr>
      <th>Closed Loop Operation</th>
      <td>
        <div v-for="(clo, index) in serverstate.clo" :key="index">
          <p>{{ clo }}</p>
        </div>
      </td>
      <td>
        <div v-for="(clo, index) in clo" :key="index">
          <input v-model="clo" type="checkbox"/>
        </div>
      </td>
    </tr>
    <tr>
      <th>Referenced</th>
      <td>
        <div v-for="refd in serverstate.referenced">
          <p>{{refd}}</p>
        </div>
      </td>
      <td>
        <div v-for="refd in referenced">
          <input v-model="refd" type="checkbox"/>
        </div>
      </td>
    </tr>
  </table>
</template>

<style scoped>

</style>