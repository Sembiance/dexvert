/* eslint-disable no-unused-vars */
import {xu, fg} from "xu";
import {XLog} from "xlog";
import {runUtil, fileUtil, printUtil, encodeUtil} from "xutil";
import {path, delay, base64Encode} from "std";
import {Program} from "../src/Program.js";
import {formats} from "../src/format/formats.js";
import {DexFile} from "../src/DexFile.js";
import {FileSet} from "../src/FileSet.js";
import {getDetections} from "../src/Detection.js";
import {programs} from "../src/program/programs.js";

const xlog = new XLog("info");

const hrm = await fileUtil.tree("/home/sembiance/tmp/out", {nodir : true});
const test = await FileSet.create("/home/sembiance/tmp/out", "output", hrm);

//await fileUtil.writeTextFile("/tmp/test.txt", await encodeUtil.decode(await Deno.readFile(Deno.args[0]), "MACINTOSH"));
//console.log(await encodeUtil.decode(await Deno.readFile(Deno.args[0]), "MACINTOSHJP"));
//console.log(await encodeUtil.decodeMacintosh({data : await Deno.readFile(Deno.args[0]), region : "japan", preserveWhitespace : true}));
