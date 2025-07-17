<script async setup lang="ts">
// sync settings from server first
import {useSettingsStore} from "@/stores/SettingsStore.ts";

const settings = useSettingsStore()
try{
  settings.syncFromServer()
}catch(e){
  window.alert("cant get settings from server :(")
}
</script>

<template>
<h1>This is the main page</h1>
<h4><router-link to="/controllers">Setup controllers</router-link></h4>

  <h4><router-link to="/stages">Stages and their statuses</router-link></h4>
</template>

<style scoped>

</style>