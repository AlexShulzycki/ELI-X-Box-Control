import {defineStore} from 'pinia'
import axios from "axios";



export const useStageStore = defineStore('AxisState', {
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
            await this.updateStageInfo()
            await this.updateStageStatus()
            await this.syncServerStageInformation()
        },
        async updateStageStatus() {
            await axios.get("/get/stage/update/status")
        },
        async updateStageInfo() {
            await axios.get("/get/stage/update/info")
        },
        async moveStage(id: number, position: number){
            let data = {
                "identifier": id,
                "position": position
            }
            const res = await axios.get("/get/stage/move/", {params: data})
            if(res.status === 200){
                return res.data as moveStageResponse
            }
        },
        async stepStage(id: number, step: number){
            let data = {
                "identifier": id,
                "step": step
            }
            const res = await axios.get("/get/stage/step/", {params: data})
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
        receiveStageInfo(info: StageInfo) {
            // check if we need to initialize a new stage
            if(this.serverStages.get(info.identifier) == undefined){
                this.serverStages.set(info.identifier, {identifier: info.identifier})
            }
            // type assertion to make the editor shut up
            let stage:FullState = <FullState>this.serverStages.get(info.identifier)
            stage.model = info.model
            stage.kind = info.kind
            stage.minimum = info.minimum
            stage.maximum = info.maximum
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

function objectToMap<type>(data:Object) {
    // This object turns a map of number: type in Object form to proper typescript Map form.
    // This is necessary because typecasting does not seem to work with maps somehow.
    // I hate typescript I hate that I have to do this manually why the hell is this a problem
    // in the first place that I have to deal with
    let res = new Map<number, type>
    Object.entries(data).forEach(([key, value]) => {
        res.set(Number(key), value as type)
    })
    return res
}


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