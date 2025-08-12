<script setup lang="ts">
import { TresCanvas } from '@tresjs/core';
import { OrbitControls, Grid } from '@tresjs/cientos';
import {useAssemblyStore} from "@/stores/AssemblyStore.ts";
import Component3D from "@/components/3D/Component3D.vue";
import {ref} from "vue";

const astore = useAssemblyStore()
const container = ref<HTMLElement>();
</script>

<template style="background-color:#efefef">
  <div id="trescontainer" ref="container">
  <TresCanvas clear-color="#82DBC5">
    <Grid
      :args="[1, 1]"
      cell-color="#000000"
      :cell-size="1"
      :cell-thickness="0.5"
      section-color="#fbb03b"
      :section-size="10"
      :section-thickness="1.3"
      :infinite-grid="true"
      :fade-from="0"
      :fade-distance="150"
      :fade-strength="1"
    />
    <TresPerspectiveCamera :position="[9, 9, 9]" />
    <OrbitControls />
    <Component3D v-for="([key, [rot, vec]], index) in astore.edits_computed_xyz_rotation" v-bind:name="key" v-bind:rot="rot" v-bind:vec="vec" v-bind:container="container" />
  </TresCanvas>
  </div>
</template>

<style scoped>
TresCanvas {
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
}
#trescontainer {
  width: 100%;
  aspect-ratio: 1;
}
</style>