<script setup lang="ts">
import {reactive, ref} from "vue";
import axios from "axios";


// input refs for the UI

const lattice_input_radio = ref("crystal")
const crystal_dropdown = ref<Crystal>()
const lattice_manual = ref()

const energy_input_radio = ref("database")
const element_dropdown = ref<Element>()
const energy_manual = ref()
const energy_line = ref()

// On load, we want to request for available crystal data and element data
interface Crystal {
  material: string,
  number: string,
  lattice_constant: number,
  name: string
}

interface Element {
  name: string,
  symbol: string,
  AbsorptionEnergy: object,
  EmissionEnergy: object,
}

// this is where we store the data
const crystals: Map<string, Crystal> = reactive(new Map<string, Crystal>())
const elements: Map<string, Element> = reactive(new Map<string, Element>())
let alignment: Alignment = reactive({
  element: {name: "None", symbol: "None", AbsorptionEnergy: {}, EmissionEnergy: {}},
  crystal: {name: "None", material: "None", number: "000", lattice_constant: 0},
  order: 0,
  height: 0,
  ThetaAbsorption: {},
  ThetaEmission: {},
  XAS_Triangles: {},
  XES_Triangles: {},
})

// this is how we fetch it (right as we load the page)
axios.get("get/geometry/CrystalData/").then((response) => {
  if (response.status === 200) {
    crystals.clear()
    Object.entries(response.data).forEach((entry) => {
      crystals.set(entry[0], entry[1] as Crystal)
    })
  } else {
    window.alert("Couldn't fetch crystal data, error: " + response.statusText);
  }

})

axios.get("get/geometry/ElementData/").then((response) => {
  if (response.status === 200) {
    elements.clear()
    Object.entries(response.data).forEach((entry) => {
      elements.set(entry[0], entry[1] as Element)
    })

  } else {
    window.alert("Couldn't fetch element data, error: " + response.statusText);
  }
})

// Process the response

interface Alignment {
  element: Element,
  crystal: Crystal,
  order: number,
  height: number,
  ThetaAbsorption: { [key: string]: number[] },
  ThetaEmission: { [key: string]: number[] },
  XAS_Triangles: { [key: string]: number[][] },
  XES_Triangles: { [key: string]: number[][] },
}

function Calculate(clickevent: Event) {
  // We look at the given inputs and decide a course of action

  // Lets generate a Crystal object
  let reqCrystal: Crystal | undefined = undefined
  if (lattice_input_radio.value == "crystal") {
    // making a non-reactive copy, I love vue
    reqCrystal = JSON.parse(JSON.stringify(crystal_dropdown.value)) as Crystal
  } else if (lattice_input_radio.value == "manual") {
    reqCrystal = {
      material: "custom",
      number: "000",
      lattice_constant: Number(lattice_manual.value),
      name: "custom"
    } as Crystal;
  }
  if (reqCrystal == undefined) {
    window.alert("Make sure the crystal input is valid")
    return
  }

  //Lets generate an Element object
  let reqElement: Element | undefined = undefined;
  if (energy_input_radio.value == "database") {
    reqElement = JSON.parse(JSON.stringify(element_dropdown.value)) as Element
  } else if (energy_input_radio.value == "manual") {
    reqElement = {
      name: "custom",
      symbol: "custom",
      AbsorptionEnergy: {},
      EmissionEnergy: {"Custom": Number(energy_manual.value)},
    } as Element;
  }

  const request = {
    element: reqElement,
    crystal: reqCrystal,
  }

  // Let the user know we're working on it...
  console.log(clickevent)
  clickevent.target.disabled = true

  // Lets generate a request!
  axios.post("post/geometry/ManualAlignment", request).then((response) => {
    if (response.status === 200) {
      clickevent.target.disabled = false
      // We need to assign the response, otherwise just replacing it loses reactivity
      Object.assign(alignment, response.data as Alignment)
    } else {
      window.alert("Calculation error: " + response.statusText);
    }
  })
}

</script>

<template>
  <div class="left_box">
    <div>
      <h3 class="subtitle">Crystal Options</h3>
      <table style="margin: auto;">
        <tbody>
        <tr>
          <td>
            <input type="radio" id="crystal_radio" value="crystal" v-model="lattice_input_radio"/>
            <label for="crystal_radio"> Crystal </label>
          </td>
          <td>
            <input type="radio" id="lattice_radio" value="manual" v-model="lattice_input_radio"/>
            <label for="lattice_radio"> Manual lattice constant </label>
          </td>
        </tr>
        <tr>
          <td>
            <select id="crystal_dropdown" v-model="crystal_dropdown">
              <option v-for="[key,crystal] in crystals.entries()" :value="crystal">{{ crystal.name }}</option>
            </select>
          </td>
          <td>
            <input type="number" id="lattice_manual_input" v-model="lattice_manual"/>
          </td>
        </tr>
        </tbody>
      </table>
    </div>
    <div>
      <h3 class="subtitle">Element Options</h3>
      <table style="margin: auto;">
        <tbody>
        <tr>
          <td>
            <input type="radio" id="database_radio" value="database" v-model="energy_input_radio"/>
            <label for="database_radio"> From Database </label>
          </td>
          <td>
            <input type="radio" id="energy_radio" value="manual" v-model="energy_input_radio"/>
            <label for="energy_radio"> Manual energy input </label>
          </td>
        </tr>
        <tr>
          <td>
            <select id="element_dropdown" v-model="element_dropdown">
              <option v-for="[key, element] in elements.entries()" :value="element">{{ element.name }}</option>
            </select>
          </td>
          <td>
            <input type="number" id="energy_manual_input" v-model="energy_manual"/> eV
          </td>
        </tr>
        </tbody>
      </table>
    </div>

    <div>
      <h3>Calculate and Choose Energy</h3>
      <button @click="Calculate($event)">Calculate</button>
      <!-- These values are fetched from the calculation -->
      <select id="energy_line" v-model="energy_line">
        <option v-if="alignment.element.EmissionEnergy != undefined"
                v-for="[line, energy] in Object.entries(alignment.element.EmissionEnergy)" :value="line">
          {{ line }}: {{ energy }}
        </option>
      </select>
      <table>
        <tbody>
        <tr>
          <th>
            n
          </th>
          <th>
            a (cm)
          </th>
          <th>
            c (cm)
          </th>
          <th>
            Theta
          </th>
        </tr>
        <!--Apparently the index starts at 1 in the v-for in vue, fantastic.-->
        <tr v-if="energy_line != undefined" v-for="order in alignment.order">
          <td>
            {{ order }}
          </td>
          <!-- apparently I cannot just do index[0], index[1], so we do a two iteration v-for -->
          <td v-if="alignment.XES_Triangles[energy_line] != undefined"
              v-for="val in alignment.XES_Triangles[energy_line][order-1] ">
            {{ Math.round(val * 100) / 1000 }}
          </td>
          <td v-if="alignment.XES_Triangles[energy_line] != undefined">
            {{ Math.round(alignment.ThetaEmission[energy_line][order - 1] * 100) / 100 }}
          </td>

        </tr>
        </tbody>
      </table>
    </div>

  </div>
  <div class="right_box">
    <canvas id="canvas"></canvas>

  </div>
</template>

<style scoped>
.left_box {
  display: flex;
  flex-direction: column;
  width: 50%;
  float: left;
  border-right: solid 2px black;
  text-align: center;
}
.right_box{
  width: auto;
  height: auto;
  padding-left: 5%;
  float: left;
  display: flex;
  flex-direction: column;

}

.subtitle {
  border-bottom: 2px solid black;
  padding-bottom: 2%;
}
</style>