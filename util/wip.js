/* eslint-disable no-unused-vars */
import {xu, fg} from "xu";
import {XLog} from "xlog";
import {runUtil, fileUtil, printUtil, encodeUtil} from "xutil";
import {path, delay, base64Encode} from "std";
import {Program} from "../src/Program.js";
import {formats} from "../src/format/formats.js";
import {DexFile} from "../src/DexFile.js";
import {getDetections} from "../src/Detection.js";
import {programs} from "../src/program/programs.js";

const xlog = new XLog("info");

await fileUtil.writeTextFile("/tmp/test.txt", await encodeUtil.decode(await Deno.readFile(Deno.args[0]), "MACINTOSH"));
//console.log(await encodeUtil.decode(await Deno.readFile(Deno.args[0]), "MACINTOSHJP"));
//console.log(await encodeUtil.decodeMacintosh({data : await Deno.readFile(Deno.args[0]), region : "japan", preserveWhitespace : true}));
