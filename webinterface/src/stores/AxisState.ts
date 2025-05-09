import {defineStore} from 'pinia'
import axios from "axios";

const api = import.meta.env.VITE_APP_API_URL;

export const useAxisStore = defineStore('AxisState', {
    state: () => {
        return {
            assemblies: [] as Assembly[],
        }
    },
    actions: {
        updateAxes(updated: Map<string, Axis>) {
            //this.axes = updated
        },
        async overwriteFromSettings() {
            const res = await axios.get(api + "SavedStagesAxes")
            console.log("SavedStagesAxes received: ")
            console.log(res)
        }
    },
    getters: {
        // return the axes from the store
        getAssemblies: (state) => {
            return state.assemblies
        },
        // Get the positions after factoring in reversal
        /*getRealPosition: (state) => {
            let res = new Map<string, number>()
            state.axes.forEach((value, key) => {
                let position = value.position
                if(value.reversed){
                    position = value.length - value.position
                }
                res.set(key, position)
            })
        }*/
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

    protected constructor(model: string, reversed: boolean, direction: string, offset: number, min: number, max: number, controller: Controller) {
        this.model = model
        this.reversed = reversed
        this.direction = direction
        this.offset = offset
        this.min = min
        this.max = max
        this.controller = controller
    }
}

export class C884Axis extends Axis {
    channel: number;

    constructor(model: string, reversed: boolean, direction: string, offset: number, min: number, max: number, controller: C884Controller, channel: number) {
        super(model, reversed, direction, offset, min, max, controller);
        this.channel = channel
    }
}

abstract class Controller {}

export class C884Controller extends Controller{
    comport: number;
    baudrate: number;

    constructor(comport: number, baudrate: number = 115200) {
        super()
        this.comport = comport
        this.baudrate = baudrate
    }
}

export class SMC5Controller extends Controller{

}

export class StandaAxis extends Axis{

}
