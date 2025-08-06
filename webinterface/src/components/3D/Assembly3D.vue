<script setup lang="ts">
import { TresCanvas } from '@tresjs/core';
import { OrbitControls } from '@tresjs/cientos';
import {useAssemblyStore} from "@/stores/AssemblyStore.ts";
import Component3D from "@/components/3D/Component3D.vue";

const astore = useAssemblyStore()
</script>

<template style="background-color:#efefef">
  <div id="trescontainer">
  <TresCanvas clear-color="#82DBC5">
    <TresPerspectiveCamera :position="[9, 9, 9]" />
    <OrbitControls />
    <Component3D v-for="([key, [rot, vec]], index) in astore.edits_computed_xyz_rotation" v-bind:name="key" v-bind:rot="rot" v-bind:vec="vec" />
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