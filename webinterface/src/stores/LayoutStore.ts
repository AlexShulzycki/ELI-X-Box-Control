import {defineStore} from "pinia";
import type {SchemaNode} from "json-schema-library";


export const useLayoutStore = defineStore("LayoutStore", {
    state: () => {
        return {
            layouts: new Map<string, WindowGrid>()
        }
    },
    actions: {

    },
    getters: {

    }
})

export enum WindowGridPayloads{
    WindowGrid = "WindowGrid",
    Stage = "Stage",
    Assembly3D = "Assembly3D",
}


export enum WindowGridOrientation{
    vertical = "vertical",
    horizontal = "horizontal",
}

export interface WindowGrid{
    orientation: WindowGridOrientation;
    components: [[string, object], [string, object]];
}