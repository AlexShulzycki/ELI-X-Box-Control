import { defineStore} from 'pinia'

export const useSettingsStore = defineStore("Settings", {
    state: () => {
        return {
            stageinfo: [] as Stage[]
        }
    },
    getters:{
        getStageInfo: (state) =>{
            return state.stageinfo
        }
    }
})

// TODO Sync this with the server
export interface Stage{
    brand: string,
    model: string,
    length: number
}

export const NOSTAGE: Stage = {
    brand: "NOSTAGE",
    model: "NOSTAGE",
    length: 0
}