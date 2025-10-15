import {defineStore} from "pinia";

export const useSettingsStore = defineStore("SettingsStore", {
    state: () => {
        return {
            websocketConnected: false
        }
    },
    actions: {

    },
    getters: {

    }
})