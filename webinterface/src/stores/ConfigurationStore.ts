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
            configurationUpdates: new Map<number, Array<ConfigurationUpdate>>(),
            // history of configuration updates for each unique config identifier
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
        async syncServerConfigState() {
            // We sync the configs from the server
            const res = await axios.get("get/ConfigState")
            if (res.status == 200) {

                // clear the current state TODO have it only edit it, so we dont mess up any front end stuff
                this.serverConfigs = parseConfigs(res.data, this.configSchemas)
                console.log("Updated current configuration state", res.data)
            }
        },
        // convoluted way to load, we are basically copying code above
        async loadConfigSet(name: string) {
            // We sync the configs from the server
            const res = await axios.get("get/loadConfiguration", {params: {name: name}})
            if (res.status == 200 && res.data.success) {
                console.log("loaded config:", res.data)
            } else if (res.status == 200 && !res.data.success) {
                console.log("Error: ", res.data)
            }

        },
        async saveCurrentConfigSet(name: string) {
            const res = await axios.get("get/saveCurrentConfiguration", {params: {name: name}})
            if (res.status == 200) {
                // Successful request, lets read the response
                console.log("received save configr response", res.data)
                console.log(res.data)
            }
        },
        async listConfigSets() {
            const res = await axios.get("get/savedConfigurations")
            if (res.status == 200) {
                return res.data.keys()
            }
        },
        async pushConfig(config: object) {
            const res = await axios.post("post/UpdateConfiguration", config)
            let responseArray: object[] = []
            if (res.status == 200) {
                // Successful request, lets read the response
                // format the data into an array explicitly
                res.data.forEach((item: object) => {
                    responseArray.push(item)
                })
                await this.syncServerConfigState()
                return responseArray
            }
        },
        async removeConfig(controllerKey: string, identifier: number) {
            const res = await axios.get("/get/RemoveConfiguration", {
                params: {
                    controllername: controllerKey,
                    identifier: identifier
                }
            })
            if (res.status != 200) {
                window.alert("Error occurred while removing config: " + res.data)
            } else {
                // All good, lets resync the status of everything
                await this.syncServerConfigState()
            }
        },
        updateConfigByID: function (config: object) {
            try {
                const id = (config as Configuration).SN
                if (this.getConfigsByID.has(id)) {
                    // go through each configuration
                    this.serverConfigs.forEach((config_list, key) => {
                        // go through the list
                        config_list.forEach((value, index) => {
                            if ((value as Configuration).SN == id) {
                                // found it, update please
                                console.log("found it")
                                config_list[index] = config
                                return
                            }
                        })
                    })
                }
            } catch (e) {
                console.log("Unable to update config: " + config)
            }
        },
        newConfigurationUpdate(update: ConfigurationUpdate) {
            console.log("configuration update", update)
            // first check if exists and the status of the queue
            // serial number is an integer, convert it
            update.SN = Number(update.SN)
            if (this.configurationUpdates.has(update.SN)) {
                // get relevant queue
                const queue = this.configurationUpdates.get(update.SN) ?? []
                // if nonexistent, empty, or last item is finished
                if ((queue.length == 0) || (queue[queue.length - 1].finished)) {
                    // overwrite with this new update
                    this.configurationUpdates.set(update.SN, [update])

                    // update configuration state if needed
                    if (update.configuration != null) {
                        this.updateConfigByID(update.configuration)
                    }
                } else {
                    // check if we indeed have a new update
                    if (queue[queue.length - 1].message != update.message) {
                        // append to the end
                        this.configurationUpdates.get(update.SN)?.push(update)

                        // update configuration state if needed
                        if (update.configuration != null) {
                            this.updateConfigByID(update.configuration)
                        }
                    }
                }
            } else {
                this.configurationUpdates.set(update.SN, [update])
            }
        }
    },
    getters: {
        getConfigWithSchema: (state) => {
            let res = new Map<string, [SchemaNode, object]>
            state.configSchemas.forEach((value, key) => {
                res.set(key, [value, state.serverConfigs.get(key) || {}])
            })
            return res
        },
        getConfigsByID: (state) => {
            let res: Map<number, object> = new Map<number, object>()
            state.serverConfigs.forEach((config_list, key) => {
                config_list.forEach((value) => {
                    try {
                        res.set((value as Configuration).SN, value)
                    } catch (e) {
                        console.log(e)
                        window.alert("Error parsing received configuration")
                    }

                })
            })
            return res
        },
        getIsUpdateQueueNotFinished: (state) => {
            let res = new Map<number, boolean>()
            state.configurationUpdates.forEach((value, key) => {
                if (value[value.length - 1].finished) {
                    res.set(key, false)
                } else {
                    res.set(key, true)
                }
            })
            return res
        }
    }
})

// update state when we wait for the response from the server
export interface responseinterface {
    identifier: number;
    success: boolean;
    error?: string;
}

export interface ConfigurationUpdate {
    SN: number;
    message: string,
    configuration?: object,
    finished: boolean,
    error: boolean
}

export interface Configuration {
    SN: number
}

function parseConfigs(data: object, schemas: Map<string, any>) {
// We sync the configs from the server

    // clear the current state
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
                    const dat = schema.getData(configState, {extendDefaults: false})
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