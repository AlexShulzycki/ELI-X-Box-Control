import {defineStore} from 'pinia'
import axios from "axios";



export const useStageStore = defineStore('AxisState', {
    state: () => {
        return {
            stageInfo: new Map<number, StageInfo>(),
            stageStatus: new Map<number, StageStatus>()

        }
    },
    actions: {
        async syncStageStatus() {
            const res = await axios.get("/stage/status")
            if(res.status === 200){
                console.log("syncing stagestatus: ", res.data)
                try{
                    this.stageStatus = objectToMap<StageStatus>(res.data)
                }catch(e){
                    console.log(e)
                    console.log("Received unusable data from server")
                }
            }
        },
        async syncStageInfo() {
            const res = await axios.get("/stage/info")
            if(res.status === 200){
                console.log("syncing stageinfo: ", res.data)
                try{
                    this.stageInfo = objectToMap<StageInfo>(res.data)
                }catch(e){
                    console.log(e)
                    console.log("Received unusable data from server")
                }

            }
        },
        async syncAll(){
            await this.syncStageInfo()
            await this.syncStageStatus()
        },
        async updateStageStatus() {
            await axios.get("/stage/update/status")
        },
        async updateStageInfo() {
            await axios.get("/stage/update/info")
        },
        async moveStage(id: number, position: number){
            let data = {
                "identifier": id,
                "position": position
            }
            const res = await axios.post("/stage/move/", data)
            if(res.status === 200){
                console.log("moving stage: "+id+" to "+position, res.data)
            }
        },
        receiveStageStatus(status: StageStatus) {
            // try to find an existing stagestatus
            if(this.stageStatus.has(status.identifier)){
                this.stageStatus.set(status.identifier, status)
            }else{
                // otherwise create a new one (completely redundant for now)
                this.stageStatus.set(status.identifier, status)
            }
        },
        receiveStageInfo(info: StageInfo) {
            // try to find an existing stagestatus
            this.stageInfo.set(info.identifier, info)
        },
        receiveStageRemoved(removed: StageRemoved){
            if(this.stageInfo.has(removed.identifier)){
                this.stageInfo.delete(removed.identifier)
            }
            if(this.stageStatus.has(removed.identifier)){
                this.stageStatus.delete(removed.identifier)
            }
        }
    },
    getters: {
        getStageInfo: (state) => {
            return state.stageInfo
        },
        getStageStatus: (state) => {
            return state.stageStatus
        },
        getConnectedStages: (state) => {
            let res: Array<number> = []
            state.stageStatus.forEach((e, i) => {
                if(e.connected){
                    res.push(e.identifier)
                }
            })
            return res
        }

    }
})

function objectToMap<type>(data:Object) {
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

export interface StageInfo{
    identifier: number
    model: string
    kind: StageKind
    minimum: number
    maximum: number
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