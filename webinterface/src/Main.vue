<script async setup lang="ts">

import XesFineAlignment from "@/components/CustomUI/XES/XES_fine_alignment.vue";

function debug() {
  console.log("debug does nothing :)")
}

</script>

<template>
  <button @click="debug()">Debug</button>
  <XesFineAlignment/>
</template>

<style scoped>

</style>