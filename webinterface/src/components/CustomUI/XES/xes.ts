// this file is for accessing localStorage for XES related stuff


export const ax_names: string[] = [
    "crystalx",
    "crystaly",
    "detectorx",
    "detectory",
    "samplex",
    "sampley",
    "detector_x_long",
    "crystal_x_long"
]

export interface localAxisSetting {
    identifier: number;
    reversed: boolean;
}

export function getSetting(key: string): null | localAxisSetting {
    const item = localStorage.getItem(key)
    if (!item) return null;
    else {
        try{
            // check if its an localaxissetting object
            const ob = JSON.parse(item) as localAxisSetting;

            // Very fucky type check, I don't like this at all
            if(ob.identifier == undefined){
                return null;
            }else{
                return ob
            }
        }catch(err){
            console.log(err)
            return null
        }

    }
}

export function saveSetting(key: string, value: localAxisSetting) {
    localStorage.setItem(key, JSON.stringify(value));
}

export function load_prepopulate(axmap: Map<string, localAxisSetting>) {
    ax_names.forEach((key) => {
        // grab value for the key
        const val = getSetting(key)
        if (!val) {
            // Not there, prepopulate with some defaults. 0 is a flag for null.
            axmap.set(key, {identifier:0, reversed:false})
            saveSetting(key, {identifier:0, reversed:false})
        } else {
            // its there, lets load it in
            try {
                axmap.set(key, val)
            } catch (e) {
                console.log(e)
            }
        }
    })
}

export function updateMapFromStorage(e: StorageEvent, map: Map<string, localAxisSetting>){

  if (!e.key || !map.get(e.key)) {
    // not relevant to us, return
    return
  } else {
    // if null then just skip
    try {
      if (!e.newValue) {
        return
      } else {
        // update the object
        map.set(e.key, JSON.parse(e.newValue) as localAxisSetting);
      }
    } catch (e) {
      console.log(e)
    }

  }
}