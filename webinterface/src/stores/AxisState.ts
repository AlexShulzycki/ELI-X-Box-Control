import { defineStore} from 'pinia'

export const useAxisState = defineStore('AxisState', {
    state: () => {
        return{
            axes: new Map<string, Axis>()
        }
    },
    actions: {
        updateAxes(updated:Map<string,Axis>) {
            this.axes = updated
        }
    },
    getters: {
        // return the axes from the store
        getAxes: (state) => {
            return state.axes
        },
        // Get the positions after factoring in reversal
        getRealPosition: (state) => {
            let res = new Map<string, number>()
            state.axes.forEach((value, key) => {
                let position = value.position
                if(value.reversed){
                    position = value.length - value.position
                }
                res.set(key, position)
            })
        }
    }
})

interface Axis {
    name: string,
    brand: string,
    model: string,
    reversed: string,
    position: number,
    length: number,
    offset: number,
    ontarget: boolean
}