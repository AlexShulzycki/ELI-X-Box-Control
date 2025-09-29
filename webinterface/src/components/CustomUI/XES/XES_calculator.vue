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
const element_energy_list = ref()

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
  element: {name: "None", symbol: "None", AbsorptionEnergy: {}, EmissionEnergy:{}},
  crystal: {name:"None", material: "None", number: "000", lattice_constant: 0},
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

interface Alignment{
  element: Element,
  crystal: Crystal,
  order: number,
  height: number,
  ThetaAbsorption: object,
  ThetaEmission: object,
  XAS_Triangles: object,
  XES_Triangles: object,
}


function Calculate() {
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

  // Lets generate a request!
  axios.post("post/geometry/ManualAlignment", request).then((response) => {
    if (response.status === 200) {
      // We need to assign the response, otherwise just replacing it loses reactivity
      Object.assign(alignment, response.data as Alignment)
    }else{
      window.alert("Calculation error: " + response.statusText);
    }
  })
}

</script>

<template>
  <div class="left_box">
    <div>
      <h3 class="subtitle">Crystal Options</h3>
      <table>
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
            <input type="number" id="lattice_manual_input" v-model="lattice_manual"/> eV
          </td>
        </tr>
        </tbody>
      </table>
    </div>
    <div>
      <h3 class="subtitle">Element Options</h3>
      <table>
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
            <input type="number" id="energy_manual_input" v-model="energy_manual"/>
          </td>
        </tr>
        <tr>
          <td>
            <!-- These values are fetched from the calculation -->
            <select id="element_energy_list" v-model="element_energy_list">
              <option v-if="alignment.element.EmissionEnergy != undefined"
                      v-for="[line, energy] in Object.entries(alignment.element.EmissionEnergy)" :value="energy">
                {{ line }}: {{ energy }}
              </option>
            </select>
          </td>
        </tr>
        </tbody>
      </table>
    </div>

    <div>
      <h3>calculate and results below</h3>
      <button @click="Calculate()">Calculate</button>
      <table>
        <tbody>
        <tr>
          <th>
            n
          </th>
          <th>
            a
          </th>
          <th>
            c
          </th>
          <th>
            Theta
          </th>
        </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>

<style scoped>
.left_box {
  display: flex;
  flex-direction: column;
}

.subtitle {
  border-bottom: 2px solid black;
  padding-bottom: 2%;
}
</style>