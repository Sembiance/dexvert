/* eslint-disable no-unused-vars */
import {xu} from "xu";
import {XLog} from "xlog";
import {runUtil, fileUtil} from "xutil";
import {path, delay, base64Encode} from "std";
import {formats, reload as reloadFormats} from "../src/format/formats.js";


const raw = await Deno.readFile("/tmp/desktop.ini");
const textDecoder = new TextDecoder();
const text = textDecoder.decode(raw);
console.log(base64Encode(text));
