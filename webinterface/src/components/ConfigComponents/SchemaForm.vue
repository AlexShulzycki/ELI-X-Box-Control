<script setup lang="ts">

import {JsonForms, type JsonFormsChangeEvent} from "@jsonforms/vue";
import {extendedVuetifyRenderers} from "@jsonforms/vue-vuetify";
import type {SchemaNode} from "json-schema-library";
import {reactive, ref, useTemplateRef} from "vue";
import {type Configuration, type responseinterface, useConfigurationStore} from "@/stores/ConfigurationStore.ts";

// Props and Emits
const {schemanode, serverdata} = defineProps<{
  schemanode: SchemaNode,
  serverdata?: Configuration
}>();
const emit = defineEmits(['success'])

// response data from server
const response = ref({identifier: -1, success: true, error: ""} as responseinterface);

// JSON forms renderer
const renderers = Object.freeze([
  ...extendedVuetifyRenderers,
  // here you can add custom renderers
]);

// Form data handling
// If formdata is not null, then it contains valid data, according to the schema
let formdata: Configuration = reactive({SN:-1})

// loading flag, informs if we are waiting for a request response
const loading = ref<boolean>(false)
const disabled = ref(false)

// On form input change, verify if the input conforms to the schema, and update formdata
const onChange = (event: JsonFormsChangeEvent) => {

  if (event.errors == undefined) {
    // check if undefined
    return
  }

  // The formdata variable also acts like a flag (SN:-1) to show if the form inputs are valid
  if (event.errors.length > 0) {
    // Form input is not schema-compliant, so clear out the form data
    formdata = {SN:-1}
  } else {
    // If there are no errors in validation, copy over the form data
    formdata = event.data;
  }
  disabled.value = formdata.SN == -1
};


// import config store to talk to the server
const configstore = useConfigurationStore()

function UpdateToServer() {
  if (formdata.SN == -1) {
    // No data to send, return.
    return;
  }

  // Format the data, {key: list[config objects, more configs, ...]},
  // in our case only one config (from the form) is in the list
  let request = {
    [schemanode.schema.title as string]: Array(formdata)
  }

  // lets change the button to loading
  loading.value = true
  // lets clear the config update queue
  configstore.configurationUpdates.set(formdata.SN, [])

  // Push the new data to the server, and read the response
  configstore.pushConfig(request).then((res) => {
    // we received a response, button is no longer loading
    loading.value = false

    if (res != undefined) {
      // Load in the response into the response var
      response.value = res[0] as responseinterface;

      // set the response id to -1 to hide the message, vary the timeouts if successful/unsuccessful
      if (response.value.success) {
        // emit a success
        emit("success", formdata.SN)
        setTimeout(() => {
          response.value.identifier = -1
        }, 3000) // 3 seconds
        // also resync the server settings
        configstore.syncServerConfigState()
      } else {
        //setTimeout(()=>{response.value.identifier = -1}, 10000) timeout unnecessary we want to see the error
      }
    }
  }, () => {
    // error
    loading.value = false
  })
}

function removeController(){
  if(serverdata != undefined){
    configstore.removeConfig(schemanode.schema.title, serverdata.SN)
  }
}

</script>

<template>
  <v-container>
    <v-card v-bind:loading="(configstore.getIsUpdateQueueNotFinished.get(formdata.SN)?? false)">
      <v-card-text>
        <v-timeline direction="horizontal"
                    v-if="formdata.SN != undefined && configstore.configurationUpdates.get(formdata.SN)" side="end">
          <v-timeline-item v-for="event in configstore.configurationUpdates.get(formdata.SN)"
                           v-bind:dot-color="event.error?'red':event.finished?'green':'orange'">
            {{ event.message }}
          </v-timeline-item>
        </v-timeline>
      </v-card-text>
      <v-card-actions>
        <v-btn @click="UpdateToServer" v-model:disabled="disabled" :loading="loading">
          Submit Changes
        </v-btn>
        <v-btn @click="removeController" v-if="serverdata.SN != null">
          Remove Controller
        </v-btn>
      </v-card-actions>
    </v-card>

    <v-alert :class="{hidden:response.success}">
      <v-alert-title>Error</v-alert-title>
      {{ response.error }}
    </v-alert>
  </v-container>
  <v-container class="myform">

    <json-forms :renderers="renderers" :schema="schemanode.schema" :data="serverdata" @change="onChange"/>
  </v-container>
</template>

<style scoped>
.hidden {
  visibility: hidden;
}
</style>