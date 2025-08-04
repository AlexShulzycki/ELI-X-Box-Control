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
            const res = await axios.get<Component>("/get/kinematics/assemblies")
            console.log("received server assembly", res.data)
            this.serverAssembly = res.data as Component
            this.overWriteEditAssembly()
        },
        overWriteEditAssembly() {
            // double make sure we are making a new copy
            this.editAssembly = JSON.parse(JSON.stringify(this.serverAssembly)) as Component
        },
        async submitEditAssembly() {
            //const req = JSON.stringify(this.editAssembly)
            const req = this.editAssembly
            console.log("sending updated assembly", req)
            const res = await axios.post("/post/kinematics/replaceRoot", req)
            if(res.status === 200) {
                console.log("Server received updated assembly", res.data)
                this.serverAssembly = res.data as Component
                this.overWriteEditAssembly()
            }
        },
        async addChild(parent: string, component: Component) {
            // check if the name is actually unique
            if (this.getEditMap?.has(component.name)) {
                console.error("Component with name", component.name, "already exists")
                window.alert("Component with name '" + component.name +"' already exists")
                return
            } else {
                this.getEditMap?.get(parent)?.children.push(component)
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
        },
        hasUnsavedEdits: (state) => {
            return !(JSON.stringify(state.serverAssembly) === JSON.stringify(state.editAssembly))
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
    attachment_point: [number, number, number]
    attachment_rotation: [number, number, number]
    children: Component[]
}

export interface Structure extends Component {
    collision_box_dimensions: [number, number, number]
    collision_box_point: [number, number, number]
}

export interface Axis extends Structure {
    axis_vector: [number, number, number]
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

function parseJSONAssembly(root: Object): Component|null {
    let res: Component = root as Component

    console.log("parseJSONAssembly", root)

    return res
}