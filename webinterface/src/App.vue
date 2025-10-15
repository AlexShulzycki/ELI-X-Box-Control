<script setup lang="ts">

import {useSettingsStore} from "@/stores/SettingsStore.ts";

const settings = useSettingsStore()
</script>

<template>
  <v-app>
    <v-navigation-drawer location="right"
                         permanent
    >
      <v-list>

        <v-list-item v-if="settings.websocketConnected" prepend-icon="mdi-lan-connect" lines="two" subtitle="Connected to server"></v-list-item>

        <v-list-item v-else prepend-icon="mdi-lan-disconnect" lines="two" subtitle="Not connected to server"></v-list-item>
      </v-list>

      <v-divider/>
      <v-list>
        <v-list-item to="/XES_setup">
          XES Axes Setup
        </v-list-item>

        <v-list-item to="XES_calculator">
          XES Geometry calculation
        </v-list-item>
        <v-list-item to="/XES">
          XES Fine Alignment
        </v-list-item>
        <v-list-item to="/HardwareConfig">
          Connect Stages
        </v-list-item>
        <v-list-item to="/stages">
          Stages and their statuses
        </v-list-item>
        <v-list-item to="/Assembly3D">
          3D Assembly
        </v-list-item>
        <v-list-item to="/AssemblyEditor">
          Assembly Editor
        </v-list-item>
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
