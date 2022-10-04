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

// this program will check all formats for all converters they use and if the family of the converter doesn't match the family of the format, then it is noted and output to console

const xlog = new XLog("info");

const PROGRAM_BASE_PATH = path.join(xu.dirname(import.meta), "..", "src", "program");
const programFamilies = Object.fromEntries((await fileUtil.tree(PROGRAM_BASE_PATH, {nodir : true, regex : /.+\/.+\.js$/i})).map(v => path.relative(PROGRAM_BASE_PATH, v)).map(v => ([path.basename(v, ".js"), path.dirname(v)])));
const otherFamilies = {};

for(const [programid, program] of Object.entries(programs))
{
	for(const [formatid, format] of Object.entries(formats))
	{
		const converters = (format.converters ? (Array.isArray(format.converters) ? format.converters : await xu.tryFallbackAsync(() => format.converters({}), [])) : []) || [];
		for(const converter of converters)
		{
			for(const converterRaw of (typeof converter==="function" ? await converter({}) : converter).split("&").map(v => v.trim()))
			{
				const {programid : converteridRaw} = Program.parseProgram(converterRaw);
				const converterid = converteridRaw.split("->")[0].trim();
				if(programFamilies[converterid]!==format.familyid)
				{
					const fullConverterid = `${programFamilies[converterid]}/${converterid}`;
					otherFamilies[fullConverterid] ||= new Set();
					otherFamilies[fullConverterid].add(format.familyid);
					xlog.info`Converter ${fullConverterid} family mismatch in format ${format.familyid}/${formatid}`;
				}
			}
		}
	}
}

console.log(otherFamilies);
