<script setup lang="ts">
import {type responseinterface, useConfigurationStore} from "@/stores/ConfigurationStore.ts";
import {ref} from "vue";

const configstore = useConfigurationStore()

// -1 is used as a flag here, if its -1 then don't display the message
const response = ref({identifier: -1, success: false, error: ""} as responseinterface);
const SN = ref()
const model = ref("8MT195, 340mm")
const min_max = ref([0,0])
const homed = ref()

function updateToServer() {

  const config = {
    "Standa":
        [{
          "SN": SN.value,
          "model": model.value,
          "connected": true,
          "min_max": min_max.value,
          "homed": homed.value,
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

</template>

<style scoped>

</style>