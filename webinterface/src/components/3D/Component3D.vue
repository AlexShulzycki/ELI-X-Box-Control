<script setup lang="ts">
import {useLoop, useTresContext} from '@tresjs/core'
import {gsap} from "gsap"
import {Quaternion, type QuaternionTuple, Vector3, type Vector3Tuple} from "three";
import {shallowRef} from "vue";

const {name, rot, vec} = defineProps<{
  name: string,
  rot: QuaternionTuple,
  vec: Vector3Tuple,
}>();

const context = useTresContext()

const posRef = shallowRef()

const { onBeforeRender } = useLoop()

onBeforeRender(({ delta }) => {
  // Compute difference in positions
  //const vecdiff = vec.sub(posRef.value.position)
  //const rotdiff = rot.invert().multiply(posRef.value.rotation)

  // TODO Fix GSAP quaternions
  gsap.to(posRef.value.position, new Vector3(vec[0], vec[1], vec[2]))
  gsap.to(posRef.value.rotation, new Quaternion(rot[0], rot[1], rot[2], rot[3]))
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