import {defineStore} from "pinia"
import axios from "axios";

export const useAssemblyStore = defineStore('AssemblyState', {
    state: () => {
        return {
            serverAssembly: structuredClone(defaultrootcomponent) as Component,
            editAssembly: structuredClone(defaultrootcomponent) as Component,
        }
    },
    actions: {
        async syncServerAssembly() {
            const res = await axios.get("/get/kinematics/assemblies")
            console.log("received server assembly", res.data)
            return
            this.overWriteEditAssembly()
        },
        overWriteEditAssembly() {
            this.editAssembly = this.serverAssembly
        },
        async updateAssembly() {
            const data = JSON.stringify(this.editAssembly)
            console.log("updating server assembly", data)
            const res = await axios.post("/get/kinematics/assemblies", data)
            console.log("received response to assembly update", res.data)
        },
        async addChild(parent: string, component: Component) {
            // check if the name is actually unique
            if (this.getEditMap?.has(component.name)) {
                console.error("Component with name", component.name, "already exists")
                return
            } else {
                this.getEditMap?.get(parent)?.children.push(component)
                console.log("Added new editable component: ", component)
            }
        }
    },
    getters: {
        getServerMap: (state) => {
            if (state.serverAssembly != null) {
                return returnMap(state.serverAssembly)
            } else {
                return null
            }
        },
        getEditMap: (state) => {
            if (state.editAssembly != null) {
                return returnMap(state.editAssembly)
            } else {
                return null
            }
        }
    }
})


export enum ComponentType {
    Component = "Component",
    Structure = "Structure",
    Axis = "Axis"
}

export interface Component {
    name: string
    type: ComponentType
    attach_to: string
    attachment_point: number[]
    attachment_rotation: number[]
    children: Component[]
}

export interface Structure extends Component {
    collision_box_dimensions: number[]
    collision_box_point: number[]
}

export interface Axis extends Structure {
    axis_vector: number[]
    axis_identifier: number
}

export function findComponentByName(name: string, root: Component): Component | undefined {
    if (root.name == name) {
        return root
    } else {
        // iterate through children
        root.children.forEach((child: Component) => {
            if (findComponentByName(name, child) != undefined) {
                return child
            }
        })
        // if we are here, the target component is not in this branch
        return undefined
    }
}

export function getParent(target: string, root: Component): Component | null {
    root.children.forEach((child: Component) => {
        // Check if our direct child is the target
        if (child.name == target) {
            // we are the parent
            return root
        } else {
            // ask the child
            const branch = getParent(target, child)
            if (branch != null) {
                // the child branch found the target
                return branch
            }
        }
    })
    // this branch didnt find the target
    return null
}

export function removeComponentByName(name: string, root: Component): boolean {
    // we could incorporate findParent(), but that would add another loop since we need to do index splicing,
    // this works, so I cant be bothered
    root.children.forEach((child: Component, index: number) => {
        if (child.name == name) {
            root.children.splice(index, 1)
            return true
        } else {
            if (removeComponentByName(name, child)) {
                return true
            }
        }
    })
    // If we are here, the target component is not on this branch
    return false
}

function returnMap(root: Component): Map<string, Component> {
    // traverses a component tree and returns a map of name: component
    let res = new Map<string, Component>()
    // add itself
    res.set(root.name, root)

    root.children.forEach((child: Component) => {
        // grab the map of the child's branch
        returnMap(child).forEach((value: Component, key: string) => {
            // update the res map with the child's map values
            res.set(key, value)
        })
    })
    // return what we got
    return res
}

const defaultrootcomponent: Component = {
    attach_to: "",
    attachment_point: [0, 0, 0],
    attachment_rotation: [0, 0, 0],
    children: [],
    name: "root",
    type: ComponentType.Component

}