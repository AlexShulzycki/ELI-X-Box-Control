<script setup lang="ts">

import type {RouteRecord} from "vue-router";

const {rootRoute, name=""} = defineProps<{ rootRoute: NestedRoute, name?: string }>()

export interface NestedRoute{
  record?:  RouteRecord,
  children: Map<string,NestedRoute>
}

</script>

<template>

  <v-list-item v-if="rootRoute.record?.path != undefined" :to="rootRoute.record.path">
    {{ rootRoute.record.name ?? rootRoute.record.path.substring(1) }}
  </v-list-item>

  <v-list-group :value="name" v-else>
    <template v-slot:activator="{ props }">
      <v-list-item v-bind="props" :title="name"/>
    </template>

    <route-v-list :rootRoute="child" :name="name" v-for="[name, child] in rootRoute.children.entries()"/>

  </v-list-group>
</template>

<style scoped>

</style>