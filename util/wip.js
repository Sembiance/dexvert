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

const v = new Uint8Array(4);
v.setUInt32BE(0, 1953790068);	// XADFileCreator
console.log(v.getString(0, 4));

v.setUInt32BE(0, 1413830740);	// XADFileType
console.log(v.getString(0, 4));


//await fileUtil.writeTextFile("/tmp/test.txt", await encodeUtil.decode(await Deno.readFile(Deno.args[0]), "MACINTOSH"));
//console.log(await encodeUtil.decode(await Deno.readFile(Deno.args[0]), "MACINTOSHJP"));
//console.log(await encodeUtil.decodeMacintosh({data : await Deno.readFile(Deno.args[0]), region : "japan", preserveWhitespace : true}));
