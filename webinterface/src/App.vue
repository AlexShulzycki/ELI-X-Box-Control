<script setup lang="ts">
import Settings from "@/components/Settings.vue";
</script>

<template>
  <header>
    <h3 style="float: left"><strong>Current route path:</strong> {{ $route.fullPath }}</h3>
    <h4 style="float: left;">
      <router-link to="/">Go Home</router-link>
      <br>
      <router-link to="/XES">XES</router-link>
      <br>
      <router-link to="/XES_setup">XES Axes Setup</router-link>
    </h4>
  </header>
  <div style="height: 100%">
    <Settings/>
  </div>
  <main>
    <div style="flex-grow: 1">
      <RouterView/>
    </div>

  </main>


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
