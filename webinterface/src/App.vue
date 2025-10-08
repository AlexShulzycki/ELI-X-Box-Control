<script setup lang="ts">
</script>

<template>
  <v-app>

    <v-navigation-drawer location="right" permanent>
      <v-list-item>
        <router-link to="/">Go Home</router-link>
      </v-list-item>
      <v-list-item>
        <router-link to="/stages">Stages and their statuses</router-link>
      </v-list-item>
      <v-list-item>

        <router-link to="/Assembly3D">3D Assembly</router-link>
      </v-list-item>
      <v-list-item>

        <router-link to="/AssemblyEditor">Assembly Editor</router-link>
      </v-list-item>
      <v-list-item>
        <router-link to="/XES">XES</router-link>
      </v-list-item>
      <v-list-item>
        <router-link to="/Settings">Settings</router-link>
      </v-list-item>
    </v-navigation-drawer>

    <v-main>
      <v-container>
        <RouterView/>
      </v-container>

    </v-main>
  </v-app>


</template>

<style scoped>

</style>
