<script setup lang="ts">
import Settings from "@/components/Settings.vue";
</script>

<template>
  <v-app>
    <v-navigation-drawer
        permanent
    >
      <v-list-item>
        <router-link to="/XES_setup">XES Axes Setup</router-link>
      </v-list-item>

      <v-list-item>
        <router-link to="XES_calculator">XES Geometry calculation</router-link>
      </v-list-item>
      <v-list-item>
        <router-link to="/XES">XES Fine Alignment</router-link>
      </v-list-item>
      <v-list-item>
        <router-link to="/HardwareConfig">Connect Stages</router-link>
      </v-list-item>

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
