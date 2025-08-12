<script setup lang="ts">

import Component3D from "@/components/3D/Component3D.vue";
import {Quaternion, type QuaternionTuple, Vector3, type Vector3Tuple} from "three";
import {useLoop} from "@tresjs/core";
import {gsap} from "gsap";
import {shallowRef} from "vue";


const {name, rot, vec, container, cbox, cpoint} = defineProps<{
  name: string,
  rot: QuaternionTuple,
  vec: Vector3Tuple,
  container: HTMLElement,
  cbox: Vector3Tuple,
  cpoint: Vector3Tuple
}>();

const cboxref = shallowRef()

const {onBeforeRender} = useLoop()

onBeforeRender(({delta}) => {
  // Compute difference in positions
  //const vecdiff = vec.sub(posRef.value.position)
  //const rotdiff = rot.invert().multiply(posRef.value.rotation)

  // TODO Fix GSAP quaternions
  cboxref.value.position = new Vector3(cpoint[0], cpoint[1], cpoint[2]);
  cboxref.value.width = cbox[0]
  cboxref.value.height = cbox[1]
  cboxref.value.length = cbox[2]
})
</script>

<template>
<Component3D v-bind:name="name" v-bind:rot="rot" v-bind:vec="vec"  :container="container" >
  <TresBoxGeometry ref="cboxref"></TresBoxGeometry>
</Component3D>
</template>

<style scoped>

</style>