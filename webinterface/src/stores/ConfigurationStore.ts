import {defineStore} from 'pinia'
import {compileSchema} from "json-schema-library"
import type {SchemaNode} from "json-schema-library"
import axios from "axios";


export const useConfigurationStore = defineStore('ConfigurationState', {
    state: () => {
        return {
            serverConfigs: new Map<number, Configuration>(),
            // Configuration on the server
            configSchemas: new Map<string, SchemaNode>(),
            // Configuration object schemas (from the server)
            loadedConfigSet: new Map<number, Configuration>(),
            // Configuration set loaded from server settings
            configurationUpdates: new Map<number, Array<ConfigurationUpdate>>(),
            // history of configuration updates for each unique config identifier
        }
    },
    actions: {

        async syncConfigSchema() {
            // We request the config schemas
            const res = await axios.get<Array<ConfigSchemaJSON>>("/get/ConfigSchema")
            console.log("syncConfigSchema", res)
            if (res.status == 200) {
                res.data.forEach((schema: ConfigSchemaJSON) => {
                    console.log("parsing received schema")
                    const node = compileSchema(schema)
                    this.configSchemas.set(schema.title, node)
                    console.log("saved received schema")
                })


            }
        },
        async syncServerConfigState() {
            // We sync the configs from the server
            const res = await axios.get<Array<Configuration>>("/get/ConfigState")
            if (res.status == 200) {
                // clear current state
                this.serverConfigs.clear()
                // parse new state
                res.data.forEach((config: Configuration) => {
                    // check if we have the schema
                    if (this.configSchemas.has(config.ControllerType)) {
                        this.serverConfigs.set(config.ID, this.configSchemas.get(config.ControllerType)?.getData(config))
                    }

                })
                console.log("Updated current configuration state", res.data)
            }
        },
        // convoluted way to load, we are basically copying code above
        async loadConfigSet(name: string) {
            // We sync the configs from the server
            const res = await axios.get("/get/loadConfiguration", {params: {name: name}})
            if (res.status == 200 && res.data.success) {
                console.log("loaded config:", res.data)
            } else if (res.status == 200 && !res.data.success) {
                console.log("Error: ", res.data)
            }

        },
        async saveCurrentConfigSet(name: string) {
            const res = await axios.get("/get/saveCurrentConfiguration", {params: {name: name}})
            if (res.status == 200) {
                // Successful request, lets read the response
                console.log("received save configr response", res.data)
                console.log(res.data)
            }
        },
        async listConfigSets() {
            const res = await axios.get("/get/savedConfigurations")
            if (res.status == 200) {
                return res.data.keys()
            }
        },
        async pushConfig(config: Configuration) {
            return await this.pushConfigs([config])
        },
        async pushConfigs(configs: Configuration[]) {
            const res = await axios.post<serverResponse[]>("/post/UpdateConfigurations", configs)
            let responseArray: serverResponse[] = []
            if (res.status == 200) {
                // Successful request, lets read the response
                // format the data into an array explicitly
                res.data.forEach((item: serverResponse) => {
                    responseArray.push(item)
                })
                await this.syncServerConfigState()
                return responseArray
            }
        },
        async removeConfig(identifier: number) {
            const res = await axios.get("/get/RemoveConfiguration", {
                params: {
                    ID: identifier
                }
            })
            if (res.status != 200) {
                window.alert("Error occurred while removing config: " + res.data)
            } else {
                // All good, lets resync the status of everything
                await this.syncServerConfigState()
            }
        },

        newConfigurationUpdate(update: ConfigurationUpdate) {
            console.log("configuration update", update)
            // first check if exists and the status of the queue
            // serial number is an integer, convert it
            update.ID = Number(update.ID)
            if (this.configurationUpdates.has(update.ID)) {
                // get relevant queue
                const queue = this.configurationUpdates.get(update.ID) ?? []
                // if nonexistent, empty, or last item is finished
                if ((queue.length == 0) || (queue[queue.length - 1].finished)) {
                    // overwrite with this new update
                    this.configurationUpdates.set(update.ID, [update])

                    // update configuration state if needed
                    if (update.configuration != null) {
                        this.serverConfigs.set(update.ID, update.configuration)
                    }
                } else {
                    // check if we indeed have a new update
                    if (queue[queue.length - 1].message != update.message) {
                        // append to the end
                        this.configurationUpdates.get(update.ID)?.push(update)

                        // update configuration state if needed
                        if (update.configuration != null) {
                            this.serverConfigs.set(update.ID, update.configuration)
                        }
                    }
                }
            } else {
                this.configurationUpdates.set(update.ID, [update])
            }
        }
    },
    getters: {

        getConfigsBySchema: (state) => {
            let res = new Map<string, Configuration[]>
            // go through each configuration
            state.serverConfigs.forEach((value, ID) => {
                // check if we have a schema for it
                const schemanode = state.configSchemas.get(value.ControllerType)
                if (schemanode != undefined) {
                        // if we have an entry in the map, push
                    if (res.get(value.ControllerType) != undefined) {
                        res.get(value.ControllerType)?.push(value)
                    } else {
                        // else create a new entry in the map
                        res.set(value.ControllerType, [value])
                    }
                }

            })
            return res
        },

        getIsUpdateQueueNotFinished: (state) => {
            let res = new Map<number, boolean>()
            state.configurationUpdates.forEach((value, key) => {
                if (value.length == 0 || value[value.length - 1].finished) {
                    res.set(key, false)
                } else {
                    res.set(key, true)
                }
            })
            return res
        }
    }
})

interface ConfigSchemaJSON {
    title: string,
}

export interface Configuration {
    ID: number,
    ControllerType: string,
}

// update state when we wait for the response from the server
export interface serverResponse {
    identifier: number;
    success: boolean;
    error?: string;
}

export interface ConfigurationUpdate {
    ID: number;
    message: string,
    configuration?: Configuration,
    finished: boolean,
    error: boolean
}
