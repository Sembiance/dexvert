/* eslint-disable no-restricted-syntax */
import {FileSet} from "/mnt/compendium/DevLab/dexvert/src/FileSet.js";

const v = await FileSet.create({primary : "/mnt/compendium/DevLab/dexvert/test/sample/image/pcx/test.pcx", aux : ["/mnt/compendium/DevLab/dexvert/test/sample/image/pcx/swinging.pcx", "/mnt/compendium/DevLab/dexvert/test/sample/image/pcx/input.pcx"]});
//const v = new FileSet({prim"/mnt/compendium/DevLab/dexvert/test/sample/image/pcx/test.pcx");
console.log(v);
