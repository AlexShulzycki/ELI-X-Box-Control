<script setup lang="ts">
import {useStageStore} from "@/stores/StageStore.ts";
import StepButton from "@/components/Stages/StepButton.vue";
import {ref} from "vue";

const {x, xrev = false, y, yrev = false} = defineProps<{
  x?: number,
  xrev?: boolean,
  y?: number,
  yrev?: boolean,
  label?: string,
}>();

const step = ref(1)

</script>

<template>
  <v-container class="fill-height">
    <!--Spawn appropriate buttons, else display message
    Directions - 0: left, 1: right, 2: up, 3: down
    -->
    <div style="aspect-ratio: 1">
      <v-row>

        <v-col style="width:50%; margin:auto">
          <StepButton v-if="y!= undefined" style="grid-column: 1; grid-row: 2" v-bind:stageid="y" :direction="2"
                      v-bind:stepby="-step" v-bind:reversed="xrev"/>
        </v-col>

      </v-row>
      <v-row>
        <v-col>
          <StepButton v-if="x!= undefined" style="grid-column: 3; grid-row: 2" v-bind:stageid="x" :direction="0"
                      v-bind:stepby="step" v-bind:reversed="xrev"/>
        </v-col>
        <v-col>
          <v-container class="fill-height" style="padding:0; margin:0">
            <h3 v-if="label != undefined" style="margin:auto">{{ label }}</h3>

            <v-number-input v-model="step" style="width: 100%" control-variant="split" label="Step (mm)" inset/>
          </v-container>

        </v-col>
        <v-col>
          <StepButton v-if="x!= undefined" style="grid-column: 2; grid-row: 1" v-bind:stageid="x" :direction="1"
                      v-bind:stepby="step" v-bind:reversed="yrev"/>
        </v-col>
      </v-row>
      <v-row>
        <v-col/>
        <v-col>
          <StepButton v-if="y!= undefined" style="grid-column: 2; grid-row: 3" v-bind:stageid="y" :direction="3"
                      v-bind:stepby="-step" v-bind:reversed="yrev" />
        </v-col>
        <v-col/>
      </v-row>
    </div>
  </v-container>
</template>

<style scoped>
</style>