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

const simpleFormats = {};

for(const [formatid, format] of Object.entries(formats))
{
	if(!Array.isArray(format.converters) || format.converters.length!==1 || format.converters[0]!=="strings")
		continue;
	
	const familyid = format.familyid;

	for(const baseKey of format.baseKeys)
		delete format[baseKey];
	delete format.baseKeys;

	const extraKeys = Object.keys(format).subtractAll(["name", "ext", "forbidExtMatch", "magic", "converters", "weakMagic", "trustMagic"]);
	if(extraKeys.length>0)
		continue;
	
	if(format.ext?.length && !format.forbidExtMatch)
		continue;
	
	if(format.ext?.length)
		continue;

	delete format.forbidExtMatch;
	delete format.converters;
	
	if(!simpleFormats[familyid])
		simpleFormats[familyid] = {};
	
	simpleFormats[familyid][formatid] = format;
}

for(const [familyid, familyFormats] of Object.entries(simpleFormats))
{
	console.log(printUtil.minorHeader(familyid));
	for(const [formatid, format] of Object.entries(familyFormats).sortMulti([([v]) => v], [false]))
		console.log(`${formatid} : ${JSON.stringify(format)},`);
}

