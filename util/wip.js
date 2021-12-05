import {xu} from "xu";
import {runUtil, fileUtil} from "xutil";
import {path} from "std";

const files = await fileUtil.tree("/home/sembiance/tmp/out");
console.log(files);
