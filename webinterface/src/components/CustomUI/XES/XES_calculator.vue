<script setup lang="ts">
import {reactive, ref, useTemplateRef} from "vue";
import axios from "axios";
import {type FullState, useStageStore} from "@/stores/StageStore.ts";
import {getSetting, type localAxisSetting} from "@/components/CustomUI/XES/xes.ts";
import TriangleView from "@/components/CustomUI/TriangleView.vue";

// stage store since we want to move the motors
const stageStore = useStageStore();

// input refs for the UI

const lattice_input_radio = ref("crystal")
const crystal_dropdown = ref<Crystal>()
const lattice_manual = ref()

const energy_input_radio = ref("database")
const element_dropdown = ref<Element>()
const energy_manual = ref()
const energy_line = ref()

const energy_dropdown = ref<Element>()
const has_server_data = ref(false)
const waiting_for_server_data = ref(false)

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
axios.get("/get/geometry/CrystalData").then((response) => {
  if (response.status === 200) {
    // load in the crystals
    crystals.clear()
    Object.entries(response.data).forEach((entry) => {
      crystals.set(entry[0], entry[1] as Crystal)
    })
  } else {
    window.alert("Couldn't fetch crystal data, error: " + response.statusText);
  }

})

axios.get("/get/geometry/ElementData").then((response) => {
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

async function Calculate() {
  // We look at the given inputs and decide a course of action

  // since this function is fired immediately on change, there is a chance that we access values before they're updated,
  // (hello vuetify select component I hate you) so we wait a tiny bit. Abysmal fix, you're welcome to find a better one.
  const delay = (delayInms:number) => {
    return new Promise(resolve => setTimeout(resolve, delayInms));
  };
  await delay(200)

  // Lets generate a Crystal object
  let reqCrystal: Crystal | undefined = undefined
  if (lattice_input_radio.value == "crystal") {
    // making a non-reactive copy, I love vue
    try {
      reqCrystal = JSON.parse(JSON.stringify(crystal_dropdown.value)) as Crystal
    } catch (e) {
      //couldn't stringify, probably not ready yet
      return
    }

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
    try {
      reqElement = JSON.parse(JSON.stringify(element_dropdown.value)) as Element
    } catch (e) {
      return
    }

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
  waiting_for_server_data.value = true
  has_server_data.value = false

  // clear the current value of the energy line so the dropdown looks empty
  energy_line.value = ""


  // Lets generate a request!
  axios.post("/post/geometry/ManualAlignment", request).then((response) => {
    if (response.status === 200) {
      // give user feedback
      waiting_for_server_data.value = false
      has_server_data.value = true

      // We need to assign the response, otherwise just replacing it loses reactivity
      Object.assign(alignment, response.data as Alignment)

    } else {
      window.alert("Calculation error: " + response.statusText);
    }
  }, ()=>{
    has_server_data.value = false
    window.alert("Error getting calculations from server")
  })

}


function RunMotors(event: Event) {

  const det: localAxisSetting | null = getSetting("detector_x_long")
  const cry: localAxisSetting | null = getSetting("crystal_x_long")

  // Get the ids of the motors from storage
  if (det == null || cry == null) {
    window.alert("Error getting settings for stages, check if you set them up properly")
    return
  }

  const det_stage: FullState | undefined = stageStore.serverStages.get(det.identifier)
  const cry_stage: FullState | undefined = stageStore.serverStages.get(cry.identifier)
  if (det_stage == undefined || cry_stage == undefined) {
    window.alert("Unable to find the stages defined in settings, make sure they're connected and set up")
    return
  }

  // if we are here, we have found the stages and they are connected

  let det_target = selected.value.c
  det_target = det_target - det.offset

  if (det.reversed && det_stage.maximum != undefined) {
    det_target = det_stage.maximum - det_target
  } else if (det.reversed) {
    window.alert("Stage does not have a maximum, can't calculate reverse value")
    return
  }

  let cry_target = Math.round(1000 * selected.value.c / 2) / 1000 // round to avoid 20 char decimals
  cry_target = cry_target - cry.offset

  if (cry.reversed && cry_stage.maximum != undefined) {
    cry_target = cry_stage.maximum - cry_target
  } else if (cry.reversed) {
    window.alert("Stage does not have a maximum, can't calculate reverse value")
    return
  }


  // final check of calculated position
  if (det_stage.minimum > det_target || det_target > det_stage.maximum) {
    window.alert("Detector out of range, cannot move to " + String(det_target))
    return
  }
  if (cry_stage.minimum > cry_target || cry_target > cry_stage.maximum) {
    window.alert("Detector out of range, cannot move to " + String(cry_target))
    return
  }

  stageStore.moveStage(det_stage.identifier, Math.round(det_target * 1000) / 1000)
  stageStore.moveStage(cry_stage.identifier, Math.round(cry_target * 1000) / 1000)

}

// Handle selecting table values

const selected = ref({a: 0, c: 0, theta: 0})

function clickTable(event: Event, order: number) {
  const a = Math.round(alignment.XES_Triangles[energy_line.value][order - 1][0] * 100) / 100
  const c = Math.round(alignment.XES_Triangles[energy_line.value][order - 1][1] * 100) / 100
  const theta = Math.round(alignment.ThetaEmission[energy_line.value][order - 1] * 100) / 100
  selected.value = {a: a, c: c, theta: theta}
  console.log(selected.value)
}

</script>

<template>
  <div class="left_box">
    <div>
      <h3 class="subtitle">Crystal Options</h3>
      <table style="margin: auto;">
        <tbody>
        <tr>
          <td colspan="2">
            <v-radio-group v-model="lattice_input_radio" inline>
              <v-radio id="crystal_radio" label="Crystal" value="crystal"/>
              <v-radio id="lattice_radio" label="Manual lattice constant" value="manual"/>
            </v-radio-group>
          </td>
        </tr>
        <tr>
          <td v-if="lattice_input_radio=='crystal'">
            <v-select @update:model-value="Calculate()" id="crystal_dropdown" v-model="crystal_dropdown"
                      v-bind:items="Array.from(crystals.values())"
                      item-title="name" return-object/>
          </td>
          <td v-else>
            <v-number-input @change="Calculate()" id="lattice_manual_input" v-model="lattice_manual"
                            control-variant="hidden"
            />
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
          <td style="column-span:2">
            <v-radio-group v-model="energy_input_radio" inline>
              <v-radio label="From Database" value="database"/>
              <v-radio label="Manual Energy Input" value="manual"/>
            </v-radio-group>
          </td>
        </tr>
        <tr>
          <td v-if="energy_input_radio=='database'">
            <v-select @update:model-value="Calculate()" id="element_dropdown" v-model="element_dropdown"
                      v-bind:items="Array.from(elements.values())"
                      item-title="name" return-object>
              <template v-slot:item="{ props: itemProps, item }">
                <v-list-item v-bind="itemProps" :title="item.raw.name" :subtitle="item.raw.symbol">
                </v-list-item>
              </template>
            </v-select>
          </td>
          <td v-else>
            <v-number-input @change="Calculate()" label="eV" type="number" control-variant="hidden"
                            id="energy_manual_input" v-model="energy_manual"/>
          </td>
        </tr>
        </tbody>
      </table>
    </div>

    <div>
      <h3>Choose Energy</h3>
      <!-- These values are fetched from the calculation. Extremely hacky implementation with vuetify, thankfully passing [0] as the value for an array of arrays selects the first item -->
      <v-select ref="energy_dropdown" v-model="energy_line"
                v-bind:items="Object.entries(alignment.element.EmissionEnergy)"
                item-value="[0]" :item-title="[0]" label="Energy Line"
                v-bind:disabled="!has_server_data" v-bind:loading="waiting_for_server_data">
        <template v-slot:item="{ props: itemProps, item }">
          <v-list-item v-bind="itemProps" :title="item.raw[0]" :subtitle="item.raw[1]"></v-list-item>
        </template>
      </v-select>
      <v-table striped="even">

        <thead>
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
        </thead>
        <tbody>
        <!--Apparently the index starts at 1 in the v-for in vue, fantastic.-->
        <tr v-if="energy_line != undefined" v-for="order in alignment.order" @click="clickTable($event, order)">
          <td>
            {{ order }}
          </td>
          <!-- apparently I cannot just do index[0], index[1], so we do a two iteration v-for TODO make this nicer-->
          <td v-if="alignment.XES_Triangles[energy_line] != undefined"
              v-for="val in alignment.XES_Triangles[energy_line][order-1] ">
            {{ Math.round(val * 100) / 1000 }}
          </td>
          <td v-if="alignment.XES_Triangles[energy_line] != undefined">
            {{ Math.round(alignment.ThetaEmission[energy_line][order - 1] * 100) / 100 }}
          </td>

        </tr>
        </tbody>
      </v-table>
    </div>

  </div>
  <div class="right_box">
    <TriangleView v-bind:a="selected.a" v-bind:c="selected.c" v-bind:theta="selected.theta"/>
    <h3>Selected Positions:</h3>
    <table style="text-align: center;">
      <tbody>
      <tr>
        <th>a (cm)</th>
        <th>c (cm)</th>
        <th>theta (degrees)</th>
      </tr>
      <tr>
        <td>{{ Math.round(selected.a * 100) / 1000 }}</td>
        <td>{{ Math.round(selected.c * 100) / 1000 }}</td>
        <td>{{ selected.theta }}</td>
      </tr>
      </tbody>
    </table>
    <v-btn @click="RunMotors($event)">Move to calculated position</v-btn>

    <div style="margin-top:40px"></div>

    <v-btn target="_blank" href="https://x-server.gmca.aps.anl.gov/cgi/www_form.exe?template=x0h_form.htm">
      Double check with x0h
    </v-btn>
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

.right_box {
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