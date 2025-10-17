import {defineStore} from "pinia";
import {useConfigurationStore} from "@/stores/ConfigurationStore.ts";
import {useStageStore} from "@/stores/StageStore.ts";



export const useSettingsStore = defineStore("SettingsStore", {
    state: () => {
        return {
            websocketConnected: false
        }
    },
    actions: {
        async websocket_got_connected() {
            this.websocketConnected = true
            const configStore = useConfigurationStore()
            await configStore.syncConfigSchema()
            await configStore.syncServerConfigState()
            const stageStore = useStageStore()
            await stageStore.syncServerStageInformation()
            await stageStore.updateStageInfo()

        }

    },
    getters: {

    }
})