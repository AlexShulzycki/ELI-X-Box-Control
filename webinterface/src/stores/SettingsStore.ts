import {defineStore} from 'pinia'
import axios from "axios";

export const useSettingsStore = defineStore("Settings", {
        state: () => {
            let pistages = new Map<string, PIStage>()
            pistages.set("NOSTAGE", NOSTAGE)
            return {
                PIStages: pistages,
                StandaStages: new Map<string, StandaStage>(),
                AssemblyStructure: {}
            }
        },
        getters: {
            getPIStageList: (state) => {
                return state.PIStages.values()
            },
            getStandaStageList: (state) => {
                return state.StandaStages.values()
            },
            PIStageMap: (state) => {
                return state.PIStages
            }
        },
        actions: {
            async syncFromServer() {
                // grab controller settings from the server
                const res = await axios.get("get/StageAxisInfo")
                if (res.status == 200) {
                    console.log("settings received: ", res.data)
                    let pidata = Object.entries(res.data.Stages.PI) as [string, PIStage][]

                    pidata.forEach((value) => {
                        // TODO allow for rotation stages
                        let stage:PIStage = {
                            model: value[0],
                            type: value[1].type,
                            length: value[1].length

                        }
                        this.PIStages.set(value[0], stage)
                    })
                    this.AssemblyStructure = res.data.Axes

                    console.log("stage info retrieved: ", this.PIStages.get("L-406.20DD10"))

                } else {
                    console.log("Error fetching settings: ", res)
                }
            }
        }
    }
)


export interface Stage {
    model: string,
    type: string,
    length?: number
}

export interface PIStage extends Stage {

}

interface StandaStage extends Stage {
    calibration: number,
    min: number,
    max: number
}

export const NOSTAGE: Stage = {
    model: "NOSTAGE",
    type: "NOSTAGE"
}