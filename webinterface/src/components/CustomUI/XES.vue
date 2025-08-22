<script setup lang="ts">

const {crystalx, crystaly, detectorx, detectory, samplex, sampley} = defineProps<{
  crystalx: number,
  crystaly: number,
  detectorx: number,
  detectory: number,
  samplex: number,
  sampley: number
}>();

// grab the stage information from the stage store


</script>

<template>
  <div style="display: grid; width: 100vw;">
    <div class="info">
      info
    </div>
    <div class="crystal">
      crystal
    </div>
    <div class="detector">
      detector
    </div>
    <div class="source">
      source
    </div>
  </div>
</template>

<style scoped>

.info {
  grid-column: 1;
  grid-row: 1;
}

.crystal {
  grid-column: 2;
  grid-row: 1;
}

.detector {
  grid-column: 3;
  grid-row: 2;
}

.source {
  grid-column: 1;
  grid-row: 2;
}

</style>