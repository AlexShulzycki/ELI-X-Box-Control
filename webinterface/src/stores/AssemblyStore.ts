import {defineStore} from "pinia"

export const useAssemblyStore = defineStore('AssemblyState', {
    state: () => {
        return {
            assemblies: new Map<string, Component>()
        }
    },
    actions: {

    },
    getters: {

    }
})


export interface XYZ{
    x: number;
    y: number;
    z: number;
}

export interface AttachmentPoint{
    point: XYZ;
    rotation: XYZ;
    attached_to: Component
}

export interface Component{
    attachments: Component;
    name: string;
    root: AttachmentPoint | null;
}

export interface AxisComponent extends Component{
    axisIdentifier: number;
    axisDirection: XYZ;
}