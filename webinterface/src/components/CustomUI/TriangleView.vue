<script setup lang="ts">
import {useTemplateRef, watchEffect} from "vue"

// props that define the triangle
const {a, c, theta, padding=20} = defineProps<{ a: number, c: number, theta: number , padding?:number}>()

// canvas
const canvas = useTemplateRef("canvas")


watchEffect(() => {
  updateCanvas()
})

function updateCanvas() {

  if (canvas.value == undefined) {
    return
  }

  // size constants
  const xmax = Number(canvas.value.width)
  const ymax = Number(canvas.value.height)
  const pad = padding * 0.01 * ymax
  const angle = Math.atan((ymax-2*pad) / (xmax/2 - pad))

  // colors
  const acolor = "blue"
  const ccolor = "green"
  const thetacolor = "orange"


  // get context, clear the canvas
  const ctx = canvas.value.getContext("2d")
  ctx.clearRect(0, 0, xmax, ymax)

  ctx.beginPath()
  ctx.strokeStyle = "black"
  // draw the border outline
  ctx.moveTo(0, 0);
  ctx.lineTo(0, ymax);
  ctx.lineTo(xmax, ymax);
  ctx.lineTo(xmax, 0)
  ctx.lineTo(0, 0)
  ctx.stroke()
  ctx.closePath()

  // now lets draw the triangle
  // C, from left to right
  ctx.beginPath()
  ctx.strokeStyle = ccolor
  ctx.moveTo(pad, ymax-pad)
  ctx.lineTo(xmax-pad, ymax-pad)
  ctx.stroke()
  ctx.closePath()

  // A from right to center
  ctx.beginPath()
  ctx.strokeStyle = acolor
  ctx.moveTo(xmax-pad, ymax-pad)
  ctx.lineTo((xmax/2), pad)
  // A from center to left
  ctx.lineTo(pad, ymax-pad)
  ctx.stroke()
  ctx.closePath()

  // Theta indicator
  ctx.beginPath()
  ctx.strokeStyle = thetacolor
  ctx.arc(pad, ymax-pad, pad, -angle, 0)
  ctx.stroke()
  ctx.closePath()
  // Second indicator on the right
  ctx.beginPath()
  ctx.arc(xmax - pad, ymax-pad, pad, -Math.PI, angle -Math.PI)
  ctx.stroke()
  ctx.closePath()

  // lets write the text
  ctx.textAlign = "center"
  ctx.textBaseline = "center"
  ctx.font = padding/1.5+"px Arial";
  ctx.fillStyle = ccolor
  ctx.fillText(c +" mm", xmax/2,ymax - pad/2);


  ctx.textAlign = "left"
  ctx.fillStyle = thetacolor
  ctx.fillText(theta+" degrees", pad*2.2, ymax-pad*1.2)

  ctx.textAlign = "right"
  ctx.fillStyle = acolor
  ctx.fillText(a+ " mm", xmax-pad*1.2, pad*2)

}


</script>


<template>

  <v-container>
    <canvas ref="canvas">

    </canvas>
  </v-container>

</template>

<style scoped>

</style>