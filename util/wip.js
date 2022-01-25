/* eslint-disable no-unused-vars */
import {xu} from "xu";
import {XLog} from "xlog";
import {runUtil, fileUtil} from "xutil";
import {path, delay} from "std";
import {formats, reload as reloadFormats} from "../src/format/formats.js";

console.log(formats.compuserveInformationManagerDB);

await delay(xu.SECOND*10);

await reloadFormats();
console.log(formats.compuserveInformationManagerDB);
