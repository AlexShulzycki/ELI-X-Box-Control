<script setup lang="ts">
import {useLoop, useTresContext} from '@tresjs/core'
import {Billboard, Box, Html, Sphere, Text3D} from '@tresjs/cientos';
import {gsap} from "gsap"
import {Quaternion, type QuaternionTuple, Vector3, type Vector3Tuple} from "three";
import {ref, shallowRef} from "vue";
import {useAssemblyStore} from "@/stores/AssemblyStore.ts";

const {name, rot, vec, container} = defineProps<{
  name: string,
  rot: QuaternionTuple,
  vec: Vector3Tuple,
  container: HTMLElement
}>();

const astore = useAssemblyStore()

const context = useTresContext()

const posRef = shallowRef()

const {onBeforeRender} = useLoop()

onBeforeRender(({delta}) => {
  // Compute difference in positions
  //const vecdiff = vec.sub(posRef.value.position)
  //const rotdiff = rot.invert().multiply(posRef.value.rotation)

  // TODO Fix GSAP quaternions
  gsap.to(posRef.value.position, new Vector3(vec[0], vec[1], vec[2]))
  gsap.to(posRef.value.rotation, new Quaternion(rot[0], rot[1], rot[2], rot[3]))
})


const comp = ref()
comp.value = astore.getEditMap.get(name)

</script>

<template id="tem">
  <TresMesh ref="posRef">
    <Sphere :args="[0.1]"/>
    <Box v-if="comp.collision_box_dimensions != undefined"
         :args="[comp.collision_box_dimensions[0], comp.collision_box_dimensions[1], comp.collision_box_dimensions[2]]"
         :position="[comp.collision_box_point[0], comp.collision_box_point[1], comp.collision_box_point[2]]"></Box>

    <Billboard>
      <Html transform center :distance-factor="11" :portal="container">
      <h3>
        {{ name }} ({{ vec[0] }}, {{ vec[1] }}, {{ vec[2] }})
      </h3>
      </Html>
    </Billboard>
  </TresMesh>
</template>

<style scoped>

</style>