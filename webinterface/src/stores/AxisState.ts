import {defineStore} from 'pinia'
import {useSettingsStore, NOSTAGE} from '@/stores/SettingsStore'
import type {Stage} from "@/stores/SettingsStore"
import axios from "axios";
import C884 from "@/components/c884.vue";

//const settingsStore = useSettingsStore()

export const useAxisStore = defineStore('AxisState', {
    state: () => {
        return {
            assemblies: [] as Assembly[],
            c884s: new Map<number, C884Controller>()
        }
    },
    actions: {
        updateAxes(updated: Map<string, Axis>) {
            //this.axes = updated
        },
        addC884(controller: C884Controller){
            this.c884s.set(controller.comport, controller)
        },
        removeController(controller: Controller){
            //Remove a controller and its associated axes
            if(controller instanceof C884Controller){
                // TODO send request to server
                this.c884s.delete(controller.comport)
            }
            // TODO implement for standa
        },
        async syncFromServer() {
            // grab controller settings from the server
            const res = await axios.get("get/SavedStageConfig")
            if(res.status == 200){
                console.log("settings received: ", res.data)

                let serverC884s = new Map<number, C884Controller>()
                // turn the c884 portion into a dict with comports as the keys
                res.data.C884.forEach((c884: C884Controller) => {serverC884s.set(c884.comport, c884)})

                // go through each c884 received, if exists, update, else, add
                serverC884s.forEach((servercontroller) =>{
                    this.c884s.set(servercontroller.comport, servercontroller)
                })

                // If we have extras, we ignore for now

            }else {
                console.log("Error fetching settings: ", res)
            }
        },
        async syncToServer(){
            await axios.post("/post/updateStageConfig", {"C884": this.c884s})
        }
    },
    getters: {
        // return the axes from the store
        getAssemblies: (state) => {
            return state.assemblies
        },
        getC884list: (state) => {
            let res: C884Controller[] = []
            state.c884s.forEach((value) => {res.push(value)})
            console.log(res)
            return res
        },
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

export class C884Controller extends Controller{
    comport: number;
    baudrate: number;
    stages: Stage[];

    constructor(comport: number, baudrate: number = 115200, stages = [NOSTAGE]) {
        super()
        this.comport = comport
        this.baudrate = baudrate
        this.stages = stages
    }
}

export class SMC5Controller extends Controller{

}

export class StandaAxis extends Axis{

}
