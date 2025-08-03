import {defineStore} from "pinia"
import axios from "axios";

export const useAssemblyStore = defineStore('AssemblyState', {
    state: () => {
        return {
            serverAssembly: new Map<string, Component>()
        }
    },
    actions: {
        async syncServerAssembly() {
            const res = await axios.get("/get/kinematics/assemblies")
            console.log("received server assembly", res.data)
        },
        async updateAssembly() {
            let data = {}
            const res = await axios.post("/get/kinematics/assemblies", data)
            console.log("updated server assembly", res.data)
        },
        async addComponent<type>(component:type){

        }
    },
    getters: {

    }
})


export enum ComponentType{
    Component = "component",
    Structure = "structure",
    Axis = "axis"
}

export interface Component {
    name: string
    type: ComponentType
    attach_to: string
    attachment_point: XYZ
    attachment_rotation: XYZ
    children: Component[]
}

export interface Structure extends Component {
    collision_box_dimensions: XYZ
    collision_box_point: XYZ
}

export interface Axis extends Structure {
    axis_vector: XYZ
    axis_identifier: number
}


export interface XYZ{
    x: number;
    y: number;
    z: number;
}
