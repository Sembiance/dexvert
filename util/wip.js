/* eslint-disable no-unused-vars */
import {xu, fg} from "xu";
import {XLog} from "xlog";
import {runUtil, fileUtil, printUtil, encodeUtil, cmdUtil} from "xutil";
import {path, delay, base64Encode, csvParse} from "std";
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

const failedFilePaths = await fileUtil.tree("/home/sembiance/Assorted/fail", {nodir : true, relative : true});
const csvResult = await xu.tryFallbackAsync(async () => await csvParse(await fileUtil.readTextFile("/home/sembiance/Assorted/formats bzr player temp delete me - Sheet1.csv")));
const extInfo = csvResult.slice(1).map(row => Object.fromEntries(row.map((v, idx) => [csvResult[0][idx].toLowerCase(), v])));

console.log(printUtil.columnizeObjects(failedFilePaths.map(failedFilePath =>
{
	const ext = path.extname(failedFilePath).toLowerCase().slice(1);
	const extInfoEntries = extInfo.filter(o => o.extensions.toLowerCase().includes(ext)).map(o => `[${o.library}] ${o.name} (${o.extensions})`);
	return {failedFilePath, ext, metaInfo : extInfoEntries.length>4 ? extInfoEntries.length : extInfoEntries.join(" ::: ")};
}).sortMulti([o => o.metaInfo.length===0, o => o.metaInfo], [false, false])));
