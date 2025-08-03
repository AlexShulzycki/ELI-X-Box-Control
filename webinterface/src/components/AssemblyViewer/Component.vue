<script setup lang="ts">
import {type Component, ComponentType, type XYZ} from "@/stores/AssemblyStore.ts"
import {ref} from "vue";

const {comp} = defineProps<{comp: Component}>()

let name = ref<string>(comp.name)
let type = ref<ComponentType>(comp.type)
let attach_to = ref<string>(comp.attach_to)
let attachment_point = ref<XYZ>({x:0, y:0, z:0})
let attachment_rotation = ref<XYZ>({x:0, y:0, z:0})
let children = ref<Component[]>(comp.children)

</script>

<template>

</template>

<style scoped>

</style>