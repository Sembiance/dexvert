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

const inputFile = {absolute : "/mnt/compendium/DevLab/dexvert/test/sample/document/gwBasic/bach", size : 1408};

async function isValid()
{
	const endBytes = (await fileUtil.readFileBytes(inputFile.absolute, Math.min(256, inputFile.size), -(Math.min(256, inputFile.size)))).reverse();
	for(const b of endBytes)
	{
		if(b===0x1A)
			return true;

		if(b===0x00)
			continue;

		break;
	}

	return false;
}


xlog.info`validEnding: ${await isValid()}`;
