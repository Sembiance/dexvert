/* eslint-disable no-unused-vars */
import {xu, fg} from "xu";
import {XLog} from "xlog";
import {runUtil, fileUtil, printUtil, encodeUtil, cmdUtil} from "xutil";
import {path, delay, base64Encode} from "std";
import {Program} from "../src/Program.js";
import {formats, init as initFormats} from "../src/format/formats.js";
import {DexFile} from "../src/DexFile.js";
import {FileSet} from "../src/FileSet.js";
import {identify} from "../src/identify.js";
import {getDetections} from "../src/Detection.js";
import {programs, init as initPrograms} from "../src/program/programs.js";
import {UInt8ArrayReader} from "UInt8ArrayReader";
import {MediaWiki} from "MediaWiki";

const xlog = new XLog("info");
//await initPrograms(xlog);
//await initFormats(xlog);

const maxPidLength = (73728).toString(36).length; // Maximum length of Deno.pid in base 36
const maxRandomIntLength = (1294).toString(36).length; // Length of 46655 in base 36
const maxCounterLength = (1294).toString(36).length; // Length of 1294 in base 36

xlog.info`${{maxPidLength, maxRandomIntLength, maxCounterLength}}`;
