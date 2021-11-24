import {xu} from "xu";
import {runUtil} from "xutil";

const r = await runUtil.run("dexvert", ["--json", "/mnt/compendium/DevLab/dexvert/test/sample/image/threeDCK/ADAM.RUN", "/home/sembiance/tmp/out/"]);
console.log({r});
