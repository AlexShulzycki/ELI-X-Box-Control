<script setup lang="ts">

import {useSettingsStore} from "@/stores/SettingsStore.ts";
import {useRouter} from "vue-router";
import RouteVList from "@/route-v-list.vue";
import {type NestedRoute} from './route-v-list.vue'

const settings = useSettingsStore()
const router = useRouter();

const routelist = router.getRoutes()

let rootNestedRoute = {children: new Map<string, NestedRoute>()} as NestedRoute;
// we must transform the list of routes into a nested object so we can display it in the nav properly.
// I scoured the documentation and apparently there is no available function in vue router that does this. incredible.

routelist.forEach(route => {
  // split the path string
  let path_string = route.path.substring(1).split('/') // we skip the first '/'
  // drill down to the correct location
  let current_location = rootNestedRoute
  path_string.forEach(folder => {
    // look if the folder is in the children of the current location
    if(current_location.children.get(folder) != undefined) {
      // enter the folder
      current_location = current_location.children.get(folder)
    }else{
      // we must create the folder and enter it
      current_location.children.set(folder, {children: new Map<string, NestedRoute>()})
      current_location = current_location.children.get(folder)
    }
  })
  // we have drilled down to the correct folder, add the route to it
  current_location.record = route
})

// sort the nav bar in the order we want
let display_nav_list:  [string, NestedRoute][] = []
rootNestedRoute.children.forEach((route, name) => {
  // skip adding the homepage
  if(name != ""){
    display_nav_list.push([name, route])
  }
})

</script>

<template>
  <v-app>
    <v-navigation-drawer location="right"
                         permanent
    >
      <v-list>

        <v-list-item v-if="settings.websocketConnected" prepend-icon="mdi-lan-connect" lines="two"
                     subtitle="Connected to server"></v-list-item>

        <v-list-item v-else prepend-icon="mdi-lan-disconnect" lines="two"
                     subtitle="Not connected to server"></v-list-item>
      </v-list>

      <v-divider/>
      <v-list>
        <route-v-list v-bind:root-route="route" :name="name" v-for="[name, route] in display_nav_list"
        :key="name"/>

        <!--
        <v-list-item to="/Assembly3D">
          3D Assembly
        </v-list-item>
        <v-list-item to="/AssemblyEditor">
          Assembly Editor
        </v-list-item>
        -->
      </v-list>

    </v-navigation-drawer>
    <v-main>
      <router-view v-slot="{ Component }">
        <keep-alive>
          <component :is="Component"/>
        </keep-alive>
      </router-view>
    </v-main>
  </v-app>
</template>

<style scoped>
header {
  display: flex;
  line-height: 1.5;
}

main {
  display: flex;
  flex-direction: row;
  background-color: aliceblue;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }
}
</style>
