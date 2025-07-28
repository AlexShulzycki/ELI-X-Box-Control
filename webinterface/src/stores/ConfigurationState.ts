import {defineStore} from 'pinia'
import {compileSchema} from "json-schema-library"
import type {SchemaNode} from "json-schema-library"
import axios from "axios";



export const useConfigurationStore = defineStore('ConfigurationState', {
    state: () => {
        return {
            configs: new Map<string, object>(),
            configSchemas: new Map<string, SchemaNode>()
        }
    },
    actions: {

        async syncConfigSchema() {
            // We request the config schemas
            const res = await axios.get("get/ConfigSchema")
            if (res.status == 200) {
                console.log("parsing received schema")
                Object.entries(res.data).forEach(([key, value]) => {
                    const node = compileSchema(value as object)
                    this.configSchemas.set(key, node)
                })
                console.log("saved received schema")
            }

        },

    }
})

function objectToMap<type>(data:Object) {
    let res = new Map<number, type>
    Object.entries(data).forEach(([key, value]) => {
        res.set(Number(key), value as type)
    })
    return res
}