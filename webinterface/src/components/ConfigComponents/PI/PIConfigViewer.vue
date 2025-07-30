<script setup lang="ts">

import {ref} from "vue";

const props = defineProps<{state: Object}>();

// variables for editing configuration
const stages= ref(props.state.stages);
const clo= ref(props.state.clo);
</script>

<template>
<table>
    <tr>
      <th>Field</th>
      <th>Current Configuration</th>
      <th>Update to</th>
    </tr>
    <tr>
      <th>Serial Number</th>
      <td>{{props.state.SN}}</td>
    </tr>
    <tr>
      <th>Stages</th>
      <td>
        <div v-for="(stage, index) in props.state.stages" key="index">
          <p>{{stage}}</p>
        </div>
      </td>
      <td>
        <div v-for="(stage, index) in stages" key="index">
          <input v-model="stage"/>
        </div>
      </td>
    </tr>
    <tr>
      <th>Closed Loop Operation</th>
      <td>
        <div v-for="(clo, index) in props.state.clo" :key="index">
          <p>{{clo}}</p>
        </div>
      </td>
      <td>
        <div v-for="(clo, index) in clo" :key="index">
          <input v-model="clo" type="checkbox"/>
        </div>
      </td>
    </tr>
  </table>
</template>

<style scoped>

</style>