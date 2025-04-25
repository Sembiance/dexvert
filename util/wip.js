/* eslint-disable no-unused-vars */
import {xu, fg} from "xu";
import {XLog} from "xlog";
import {runUtil, fileUtil, printUtil, encodeUtil, cmdUtil, hashUtil} from "xutil";
import {path, delay, base64Encode, csvParse, ascii85Decode} from "std";
import {Program} from "../src/Program.js";
import {formats, init as initFormats} from "../src/format/formats.js";
import {DexFile} from "../src/DexFile.js";
import {FileSet} from "../src/FileSet.js";
import {identify, getMacBinaryMeta} from "../src/identify.js";
import {getDetections} from "../src/Detection.js";
import {programs, init as initPrograms} from "../src/program/programs.js";
import {UInt8ArrayReader} from "UInt8ArrayReader";
import {MediaWiki} from "MediaWiki";
import {xmlParse} from "denoLandX";
import {DEXRPC_HOST, DEXRPC_PORT} from "../src/dexUtil.js";
import {WEAK_VALUES} from "../src/WEAK.js";

const xlog = new XLog("info");

await initPrograms(xlog);
await initFormats(xlog);
