<script setup lang="ts">
import {type WindowGrid, WindowGridOrientation, WindowGridPayloads} from "@/stores/LayoutStore.ts";
import {watch, ref} from "vue";

const {windowgrid} = defineProps<{ windowgrid: WindowGrid }>();

const emit = defineEmits(['changetree'])

const WGprop1 = ref<WindowGrid>({
  orientation: WindowGridOrientation.horizontal,
  components: [["empty", {}],["empty", {}]]
})

const WGprop2 = ref<WindowGrid>({
  orientation: WindowGridOrientation.horizontal,
  components: [["empty", {}],["empty", {}]]
})

function saveLayout() {
  window.alert('implement pls')
}

let isHorizontal = ref(true) // toggles orientation
let knownTree = ref(windowgrid) // stores what we know about this state and any child window grids

function removeSelf(which: number) {
  windowgrid.components[which] = ["empty", {}]
}

function emitChildConfigs(){
  emit("changetree", knownTree.value)
}

function receiveChildConfig1(value){
  knownTree.value.components[0][1] = value
  emitChildConfigs()
}
function receiveChildConfig2(value){
  knownTree.value.components[1][1] = value
  emitChildConfigs()
}

watch(windowgrid.components, (old, newvalue) => {
  if(old[0] != newvalue[0]){
    console.log("slot 1 changed")
    knownTree.value.components[0] = newvalue[0]
  }
  if(old[1] != newvalue[1]){
    console.log("slot 2 changed")
    knownTree.value.components[1] = newvalue[1]
  }
  // emit the update
  emitChildConfigs()
})

</script>

<template>
  <div class="options">
    <button @click="saveLayout()">Save Layout</button>
    <button @click="isHorizontal = !isHorizontal">Switch Orientation</button>

  </div>
  <div class="windowgrid" :class="{horizontal : isHorizontal, vertical: !isHorizontal}">
    <div v-if="windowgrid.components[0][0] != 'empty'" class="one">
      <button @click="removeSelf(0)">Remove</button>
      <component v-if="windowgrid.components[0][0] != 'WindowGrid'" v-bind:is="windowgrid.components[0][0]" v-model="windowgrid.components[0][1]"/>
      <WindowGrid v-else-if="windowgrid.components[0][0] == 'WindowGrid'" v-model:windowgrid="WGprop1"
      @changetree="receiveChildConfig1"/>
    </div>
    <div v-else>
      <select v-model="windowgrid.components[0][0]">
        <option v-for="op in WindowGridPayloads" v-bind:value="op">{{op}}</option>
      </select>
    </div>
    <div v-if="windowgrid.components[1][0] != 'empty'" class="two">
      <button @click="removeSelf(1)">Remove</button>
      <component v-if="windowgrid.components[1][0] != 'WindowGrid'"
                 v-bind:is="windowgrid.components[1][0]" v-model="windowgrid.components[0][1]"/>
      <WindowGrid v-else-if="windowgrid.components[1][0] == 'WindowGrid'" v-model:windowgrid="WGprop2"
      @changetree="receiveChildConfig2"/>
    </div>
    <div v-else>
      <select v-model="windowgrid.components[1][0]">
        <option v-for="op in WindowGridPayloads" v-bind:value="op">{{op}}</option>
      </select>
    </div>
  </div>
</template>

<style scoped>

template {
  width: 100%;
  height: 100%;
}

.windowgrid {
  display: flex;
  width: 100%;
  height: 100%;
}
.horizontal{
  flex-direction: row;
}
.vertical{
  flex-direction: column;
}

</style>