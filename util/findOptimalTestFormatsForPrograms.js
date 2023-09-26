/* eslint-disable no-unused-vars */
import {xu, fg} from "xu";
import {XLog} from "xlog";
import {runUtil, fileUtil, printUtil, encodeUtil} from "xutil";
import {path, delay, base64Encode} from "std";
import {Program} from "../src/Program.js";
import {formats, init as initFormats} from "../src/format/formats.js";
import {DexFile} from "../src/DexFile.js";
import {FileSet} from "../src/FileSet.js";
import {getDetections} from "../src/Detection.js";
import {programs, init as initPrograms} from "../src/program/programs.js";

const xlog = new XLog("info");
await initPrograms(xlog);
await initFormats(xlog);

const programFormats = {};
const finalProgramFormats = {};

for(const [programid, program] of Object.entries(programs))
{
	if(program.loc!=="gentoo")
		continue;

	programFormats[programid] = [];

	for(const [formatid, format] of Object.entries(formats))
	{
		if(format.unsupported)
			continue;

		const converters = (format.converters ? (Array.isArray(format.converters) ? format.converters : await xu.tryFallbackAsync(() => format.converters({}), [])) : []) || [];
		const converterids = [];
		for(const converter of converters)
		{
			for(const converterRaw of (typeof converter==="function" ? await converter({}) : converter).split("&").map(v => v.trim()))
			{
				const {programid : converteridRaw} = Program.parseProgram(converterRaw);
				converterids.push(converteridRaw.split("->")[0].trim());
			}
		}

		for(let i=0;i<converterids.length;i++)
		{
			if(converterids[i]===programid)
			{
				programFormats[programid].push({formatid, familyid : format.familyid, loc : i, count : converterids.length});
				break;
			}
		}
	}
}

for(const [programid, converters] of Object.entries(programFormats))
{
	for(let i=0;i<20;i++)
	{
		for(let count=1;count<20;count++)
		{
			for(const converter of converters)
			{
				if(converter.count===count && converter.loc===i)
				{
					finalProgramFormats[programid] = `${converter.familyid}/${converter.formatid}`;
					break;
				}
			}

			if(finalProgramFormats[programid])
				break;
		}

		if(finalProgramFormats[programid])
			break;
	}
}

const winXPPrograms = new Set(Object.keys(finalProgramFormats).sortMulti());

console.log(finalProgramFormats);
console.log(winXPPrograms);
console.log(Object.values(finalProgramFormats).unique().sortMulti().join("\n"));

const DATA_FILE_PATH = path.join(xu.dirname(import.meta), "..", "test", "testExpected.json");
const testData = xu.parseJSON(await fileUtil.readTextFile(DATA_FILE_PATH), {});

for(const [formatAndFile, data] of Object.entries(testData))
{
	if(winXPPrograms.has(data.converter))
	{
		const parts = formatAndFile.split("/");
		//console.log(data.converter);
		console.log(`./testdexvert --skipBuild --format=${parts[0]}/${parts[1]} --file="${parts[2]}"`);
		winXPPrograms.delete(data.converter);
	}
}
