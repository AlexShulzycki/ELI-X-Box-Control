import {defineStore} from 'pinia'
import axios from "axios";



export const useDeviceStore = defineStore('DeviceState', {
    state: () => {
        return {
            serverStages: new Map<number, FullState>()
        }
    },
    actions: {
        async syncServerStageInformation() {
            const res = await axios.get("/get/stage/fullstate")
            if(res.status === 200){
                const data = objectToMap<FullState>(res.data)
                console.log("received new stage state: ", data)
                // update existing and add new
                data.forEach((stage: FullState) => {
                    this.serverStages.set(stage.identifier, stage)
                })
                // remove non-existing
                this.serverStages.forEach(stage => {
                    if(data.get(stage.identifier) == undefined) {
                        this.serverStages.delete(stage.identifier)
                    }
                })

            }
        },
        async fullRefresh(){


        },
        async moveStage(id: number, position: number){
            let data = {
                "identifier": id,
                "position": position
            }
            const res = await axios.get("/get/stage/move", {params: data})
            if(res.status === 200){
                return res.data as moveStageResponse
            }
        },
        async stepStage(id: number, step: number){
            let data = {
                "identifier": id,
                "step": step
            }
            const res = await axios.get("/get/stage/step", {params: data})
            if(res.status === 200){
                return res.data as moveStageResponse
            }
        },
        receiveStageStatus(status: StageStatus) {
            // check if we need to initialize a new stage
            if(this.serverStages.get(status.identifier) == undefined) {
                this.serverStages.set(status.identifier, {identifier: status.identifier})
            }
            // type assertion to make the editor shut up
            let stage:FullState = <FullState>this.serverStages.get(status.identifier)

            stage.connected = status.connected
            stage.ready = status.ready
            stage.position = status.position
            stage.ontarget = status.ontarget

            this.serverStages.set(stage.identifier, stage)
        },

        receiveStageRemoved(removed: StageRemoved){
            if(this.serverStages.has(removed.identifier)){
                this.serverStages.delete(removed.identifier)
            }
        }
    },
    getters: {
        getStageIDs: (state) => {
            let res: Array<number> = []
            state.serverStages.forEach((e, key) => {
                    res.push(e.identifier)
            })
            return res
        },

    }
})


enum StageKind{
    rotational = "rotational",
    linear = "linear"
}

export interface FullState{
    identifier: number
    model?: string
    kind?: StageKind
    minimum?: number
    maximum?: number
    connected?: boolean
    ready?: boolean
    position?: number
    ontarget?: boolean
}

export interface StageInfo {
    identifier: number
    model: string
    kind: StageKind
    minimum?: number
    maximum?: number
}

export interface StageStatus{
    identifier: number
    connected: boolean
    ready: boolean
    position: number
    ontarget: boolean
}

export interface StageRemoved {
    identifier: number
}


export interface moveStageTo{
    identifier: number,
    position: number
}
export interface moveStageResponse{
    success: boolean,
    error?: string
}


