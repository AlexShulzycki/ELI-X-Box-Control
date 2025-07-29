import {defineStore} from 'pinia'
import {compileSchema} from "json-schema-library"
import type {SchemaNode} from "json-schema-library"
import axios from "axios";



export const useConfigurationStore = defineStore('ConfigurationState', {
    state: () => {
        return {
            serverConfigs: new Map<string, Array<object>>(),
            configSchemas: new Map<string, SchemaNode>(),
            updateConfigs: new Map<string, Array<object>>(),
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
        async syncServerConfigState(){
            // We sync the configs from the server
            const res = await axios.get("get/ConfigState")
            if (res.status == 200) {
                console.log("parsing received config state")

                // clear the current state
                this.serverConfigs.clear()

                // iterate through each config type
                Object.entries(res.data).forEach(([key, value]) => {
                    let schema = this.configSchemas.get(key)
                    if(schema != undefined) {

                        // result array
                        let res: Object[] = []

                        // try to parse the list of configs according to the schema
                        try {
                            (value as Array<object>).forEach((configState) => {
                                res.push(schema.getData(configState))
                            })

                            // all done, save the parsed settings
                            this.serverConfigs.set(key, res)

                        } catch (e) {
                            console.log("Error parsing data for " + key)
                        }

                    }
                })
                console.log("Updated current configuration state")
            }
        },
        async pushUpdateConfigState(){
            // Pushes contents of updateConfigs to the server
            const res = await axios.post("post/UpdateConfiguration", this.updateConfigs)
            if(res.status == 200) {
                // Successful request, lets read the response
                console.log("received update state: " + res.data)
            }
        }
    },
    getters: {
        getSchemaNodes: (state) => {
            return state.configSchemas
        },
        getCurrentConfig: (state) => {
            let res = new Map<string, object>()
            state.serverConfigs.forEach((value: Array<object>, key) => {
                // get the schema for the type of config (denoted by the key)
                let schema = state.configSchemas.get(key)
                if(schema != undefined){
                    // try to parse the list of configs according to the schema
                    console.error("Not ready to parse, implement this method please")
                    try{
                        value.forEach((item) => {
                        //TODO Finish this up
                        })
                        res.set(key, schema.getData(value))
                    }catch (e){
                        console.log("Error parsing data for "+ key)
                    }
                }
            })
            return res
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