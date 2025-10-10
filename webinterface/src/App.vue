<script setup lang="ts">
</script>

<template>
  <v-app>

    <v-navigation-drawer location="right" permanent>
      <v-list-item to="/">
        Go Home
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
      <v-list-item to="/XES">
        XES
      </v-list-item>
      <v-list-item to="/Settings">
        Settings
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
