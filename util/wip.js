/* eslint-disable no-unused-vars */
import {xu, fg} from "xu";
import {XLog} from "xlog";
import {runUtil, fileUtil, printUtil} from "xutil";
import {path, delay, base64Encode} from "std";
import {Program} from "../src/Program.js";
import {formats, reload as reloadFormats} from "../src/format/formats.js";
import {DexFile} from "../src/DexFile.js";
import {getDetections} from "../src/Detection.js";
import {programs} from "../src/program/programs.js";

const xlog = new XLog("info");

