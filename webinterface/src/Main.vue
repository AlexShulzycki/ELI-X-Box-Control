<script async setup lang="ts">

import XES from "@/components/CustomUI/XES/XES.vue";

function debug() {
  console.log("debug does nothing :)")
}

</script>

<template>
  <button @click="debug()">Debug</button>
  <XES/>
</template>

<style scoped>

</style>