<script async setup lang="ts">

import {useLayoutStore, WindowGridOrientation} from "@/stores/LayoutStore.ts";
import WindowGrid from "@/components/Layout/WindowGrid.vue";
import {ref} from "vue";

const lstore = useLayoutStore()

lstore.layouts.set("default", {
  orientation: WindowGridOrientation.horizontal,
  components: [["empty", {}], ["empty", {}]]
})

const deflayout = lstore.layouts.get('default')

</script>

<template>
<h1>This is the main page</h1>
    <WindowGrid v-if="deflayout != undefined" v-bind:windowgrid="deflayout"/>
</template>

<style scoped>

</style>