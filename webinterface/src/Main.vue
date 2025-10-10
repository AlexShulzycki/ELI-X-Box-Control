<script async setup lang="ts">


function debug() {
  console.log("debug does nothing :)")
}

</script>

<template>
  <v-btn @click="debug()">Debug</v-btn>
<h1>This is the main page</h1>
  <!--
    <WindowGrid v-if="deflayout != undefined" v-bind:windowgrid="deflayout" @changetree="save_default"/>
    -->
</template>

<style scoped>

  WindowGrid{
    width:100vw;
    flex-grow: 1;
  }
</style>