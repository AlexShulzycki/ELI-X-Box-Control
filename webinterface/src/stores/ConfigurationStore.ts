import {defineStore} from 'pinia'
import {compileSchema} from "json-schema-library"
import type {SchemaNode} from "json-schema-library"
import axios from "axios";



export const useConfigurationStore = defineStore('ConfigurationState', {
    state: () => {
        return {
            serverConfigs: new Map<string, Array<object>>(),
            // Configuration on the server
            configSchemas: new Map<string, SchemaNode>(),
            // Configuration object schemas (from the server)
            loadedConfigSet: new Map<string, Array<object>>(),
            // Configuration set loaded from server settings
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

                // clear the current state TODO have it only edit it, so we dont mess up any front end stuff
                this.serverConfigs = parseConfigs(res.data, this.configSchemas)
                console.log("Updated current configuration state", res.data)
            }
        },
        // convoluted way to load, we are basically copying code above
        async loadConfigSet(name:string){
            // We sync the configs from the server
            const res = await axios.get("get/loadConfiguration", {params:{name: name}})
            if (res.status == 200 && res.data.success) {
                console.log("loaded config:", res.data)
            }else if(res.status == 200 && !res.data.success){
                console.log("Error: ", res.data)
            }

        },
        async saveCurrentConfigSet(name: string){
            const res = await axios.get("get/saveCurrentConfiguration", {params:{name: name}})
            if(res.status == 200) {
                // Successful request, lets read the response
                console.log("received save configr response", res.data)
                console.log(res.data)
            }
        },
        async listConfigSets(){
            const res = await axios.get("get/savedConfigurations")
            if(res.status == 200) {
                return res.data.keys()
            }
        },
        async pushConfig(config: object) {
            const res = await axios.post("post/UpdateConfiguration", config)
            let responseArray: object[] = []
            if(res.status == 200) {
                // Successful request, lets read the response
                console.log("received update response to update request", res.data, config)
                // format the data into an array explicitly
                res.data.forEach((item: object) => {
                    responseArray.push(item)
                })
                await this.syncServerConfigState()
                return responseArray
            }
        },
        async removeConfig(controllerKey: string, identifier:number){
            const res = await axios.get("/get/RemoveConfiguration", {params: {controllername: controllerKey, identifier: identifier}})
            if(res.status != 200){
              window.alert("Error occurred while removing config: " + res.data)
            }else{
              // All good, lets resync the status of everything
              await this.syncServerConfigState()
            }
        }
    },
    getters: {
        getSchemaNodes: (state) => {
            return state.configSchemas
        },
        getServerConfigs: (state) => {
            return state.serverConfigs
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

function objectToMap<type1, type2>(data:Object) {
    let res = new Map<type1, type2>
    Object.entries(data).forEach(([key, value]) => {
        res.set(key as type1 , value as type2)
    })
    return res
}

// update state when we wait for the response from the server
export interface responseinterface {
  identifier: number;
  success: boolean;
  error?: string;
}

export interface settingsresponseinterface {
    success: boolean
    error: string
    configuration: Map<string, object>
}

function parseConfigs(data:object, schemas:Map<string, any>) {
// We sync the configs from the server

        // clear the current state TODO have it only edit it, so we dont mess up any front end stuff
        let finalres = new Map<string, Array<object>>()

        // iterate through each config type
        Object.entries(data).forEach(([key, value]) => {
            let schema = schemas.get(key)
            if (schema != undefined) {

                // result array
                let res: Object[] = []

                // try to parse the list of configs according to the schema
                try {
                    (value as Array<object>).forEach((configState) => {
                        const dat = schema.getData(configState)
                        res.push(dat)
                    })

                    // all done, save the parsed settings
                    finalres.set(key, res)

                } catch (e) {
                    console.log("Error parsing data for " + key)
                }

            }
        })
        return finalres

}