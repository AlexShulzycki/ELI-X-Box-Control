<script async setup lang="ts">

import {useLayoutStore, WindowGridOrientation} from "@/stores/LayoutStore.ts";
import WindowGrid from "@/components/Layout/WindowGrid.vue";

const lstore = useLayoutStore()

lstore.layouts.set("default", {
  orientation: WindowGridOrientation.horizontal,
  components: [["Assembly3D", {}], ["empty", {}]]
})

const deflayout = lstore.layouts.get('default')

function debug(){
  deflayout.components[1] = ["Assembly3D", {}]
}

</script>

<template>
  <button @click="debug()">Debug</button>
<h1>This is the main page</h1>
    <WindowGrid v-if="deflayout != undefined" v-bind:windowgrid="deflayout" @changetree="console.log"/>
</template>

<style scoped>

</style>