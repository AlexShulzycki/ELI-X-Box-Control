import {defineStore} from 'pinia'
import {useSettingsStore, NOSTAGE, type PIStage} from '@/stores/SettingsStore'
import type {Stage} from "@/stores/SettingsStore"
import axios from "axios";



export const useAxisStore = defineStore('AxisState', {
    state: () => {
        return {
            c884config: new Map<number, C884Config>()

        }
    },
    actions: {
        updateAxes(updated: Map<string, Axis>) {
            //this.axes = updated
        },
        addC884(controller: C884Config){
            this.c884config.set(controller.comport, controller)
        },
        removeController(comport: number){
            //Remove a controller and its associated axes
            // TODO send request to server
            this.c884config.delete(comport)

            // TODO implement for standa
        },
        async syncFromServer() {
            // grab controller settings from the server
            const res = await axios.get("get/SavedStageConfig")
            if(res.status == 200){
                console.log("settings received: ", res.data)

                let serverconfig = new Map<number, C884Config>()
                // Put the c884 portion of the response into a dict with comports as the keys
                res.data.C884.forEach((c884: C884Config) => {serverconfig.set(c884.comport, c884)})

                // go through each c884 received, if exists, update, else, add
                serverconfig.forEach((servercontroller) =>{
                    this.c884config.set(servercontroller.comport, servercontroller)
                })

                // If we have extras, we ignore for now

            }else {
                console.log("Error fetching settings: ", res)
            }
        },
        async syncToServer(){
            await axios.post("/post/updateStageConfig", {"C884": this.c884config})
        }
    },
    getters: {
        getC884configs: (state) => {
            let res: C884Config[] = []
            state.c884config.forEach((value) => {
                res.push(value)
            })
            return res
        },
        getC884objects: (state) => {
            let res: C884Controller[] = []
            const set = useSettingsStore()
            state.c884config.forEach((config) => {
                let stages:Stage[] = []
                config.stages.forEach((stagename) => {
                    stages.push(set.PIStageMap.get(stagename) as Stage)
                })
                res.push(new C884Controller(config, stages))
            })
            return res
        }

    }
})

export interface Assembly {
    name: string,
    points: Point[]
}

export interface Point {
    name: string,
    axes: Axis[]

}

abstract class Axis {
    model: string;
    reversed: boolean;
    direction: string;
    offset: number;
    min: number;
    max: number;
    controller: Controller;
    ready: boolean

    protected constructor(model: string, reversed: boolean, direction: string, offset: number, min: number, max: number, controller: Controller) {
        this.model = model
        this.reversed = reversed
        this.direction = direction
        this.offset = offset
        this.min = min
        this.max = max
        this.controller = controller
        this.ready = false
    }
}

export class C884Axis extends Axis {
    channel: number;

    constructor(model: string, reversed: boolean, direction: string, offset: number, min: number, max: number, controller: C884Controller, channel: number) {
        super(model, reversed, direction, offset, min, max, controller);
        this.channel = channel
    }
}

abstract class Controller {
    ready: boolean

    constructor() {
        this.ready = false
    }
}

export interface C884Config {
    comport: number;
    baudrate: number;
    stages: string[];
}

export class C884Controller extends Controller{
    config: C884Config;
    stages: Stage[];

    constructor(config: C884Config, stages = [NOSTAGE, NOSTAGE, NOSTAGE, NOSTAGE]) {
        super()
        this.config = config
        this.stages = stages
    }
}

export class SMC5Controller extends Controller{

}

export class StandaAxis extends Axis{

}
