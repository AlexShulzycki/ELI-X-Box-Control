<script setup lang="ts">
import {useLoop, useTresContext} from '@tresjs/core'
import {gsap} from "gsap"
import type {Quaternion, Vector3} from "three";
import {shallowRef} from "vue";

const {name, rot, vec} = defineProps<{
  name: string,
  rot: Quaternion,
  vec: Vector3,
}>();

const context = useTresContext()

const posRef = shallowRef()

const { onBeforeRender } = useLoop()

onBeforeRender(({ delta }) => {
  // Compute difference in positions
  const vecdiff = vec.sub(posRef.value.position)
  const rotdiff = rot.invert().multiply(posRef.value.rotation)

  gsap.to(posRef.value.position, vec)
  gsap.to(posRef.value.rotation, rot)
})
</script>

<template>
  <TresMesh ref="posRef">
      <TresSphereGeometry />
      <TresMeshToonMaterial color="#FBB03B" />

    </TresMesh>
</template>

<style scoped>

</style>