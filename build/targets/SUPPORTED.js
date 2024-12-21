import {xu} from "xu";
import {fileUtil} from "xutil";
import {path} from "std";
import {formats, init as initFormats} from "../../src/format/formats.js";
import {DexState} from "../../src/DexState.js";
import {DexFile} from "../../src/DexFile.js";
import {FileSet} from "../../src/FileSet.js";
import {Identification} from "../../src/Identification.js";
import {programs, init as initPrograms} from "../../src/program/programs.js";

const SAMPLES_DIR_PATH = path.join(import.meta.dirname, "..", "..", "test", "sample");

const DUMMY_FILE_PATH = await fileUtil.genTempPath();
await fileUtil.writeTextFile(DUMMY_FILE_PATH, "x");
const DUMMY_DIR_PATH = await fileUtil.genTempPath();
await Deno.mkdir(DUMMY_DIR_PATH);

export default async function SUPPORTED(xlog)
{
	await initPrograms(xlog);
	await initFormats(xlog);

	const supportedFormats = Object.fromEntries(Object.entries(formats).filter(([, format]) => !format.unsupported));

	xlog.info`Writing SUPPORTED.md to disk...`;
	await fileUtil.writeTextFile(path.join(import.meta.dirname, "..", "..", "SUPPORTED.md"), `# Supported File Formats (${Object.keys(supportedFormats).length.toLocaleString()})
Converters are in priority order. That is, early converter entries handle the format better than later converters.

Extensions are in order of importance, with the format's primary extension appearing first.

${(await Object.values(supportedFormats).map(f => f.familyid).unique().sortMulti().parallelMap(async familyid => `

## ${familyid.toProperCase()} (${Object.values(supportedFormats).filter(f => f.familyid===familyid).length.toLocaleString()})
Family | Name | Extensions | Converters | Notes
------ | ---- | ---------- | ---------- | -----
${(await Object.values(supportedFormats).filter(f => f.familyid===familyid).sortMulti(f => f.name).parallelMap(async f =>
	{
		const noteParts = [];
		let formatSampleDirPath = path.join(SAMPLES_DIR_PATH, `${f.familyid}/${f.formatid}`);
		if(!await fileUtil.exists(formatSampleDirPath))
			formatSampleDirPath = path.join(SAMPLES_DIR_PATH, `unsupported/${f.formatid}`);
		if(await fileUtil.exists(formatSampleDirPath))
		{
			const formatSamples = await fileUtil.tree(formatSampleDirPath);
			noteParts.push(`[${formatSamples.length.toLocaleString()} sample file${formatSamples.length===1 ? "" : "s"}](https://sembiance.com/fileFormatSamples/${path.relative(SAMPLES_DIR_PATH, formatSampleDirPath)}/)`);
		}

		let converters = [];
		if(f.converters)
		{
			const id = Identification.create({from : "dexvert", confidence : 100, magic : f.name});
			const dexState = DexState.create({original : {input : await DexFile.create(DUMMY_FILE_PATH), output : await DexFile.create(DUMMY_DIR_PATH)}, ids : [id]});
			dexState.startPhase({id, format : f, f : await FileSet.create(path.dirname(DUMMY_FILE_PATH), "input", dexState.original.input)});
			dexState.meta.yes = true;

			converters = typeof f.converters==="function" ? await f.converters(dexState) : f.converters;
			if(converters.some(v => Array.isArray(v)))
				converters = converters.flatMap(converter => (typeof converter==="function" ? converter(dexState) : converter)).unique();
			converters = converters.map(converter => (typeof converter==="function" ? converter(dexState) : converter));
			converters = converters.map(converter => converter.split("->")[0].trim().split("[")[0].trim());	// get rid of chains
			converters = converters.flatMap(converter => converter.split("&").map(v => v.trim())).unique();	// expand out those that call multiple programs at once and remove duplicates (image/fig (XFig) for example)
			converters = converters.map(programid => (programs[programid] ? (programs[programid].website ? `[${programid}](${programs[programid].website})` : programid) : programid));
		}
		
		const noteText = (f.notes || "").replaceAll("\n", " ").trim();
		if(noteText && noteText.length>0)
			noteParts.push(noteText);
		return (`${f.familyid} | ${f.website ? `[${f.name}](${f.website})` : f.name} | ${(f.ext || []).join(" ")} | ${(converters || []).join(" ")} | ${noteParts.join(" - ")}`);
	})).join("\n")}
`)).join("\n")}
`);

	xlog.info`Cleaning up...`;
	await fileUtil.unlink(DUMMY_FILE_PATH);
	await fileUtil.unlink(DUMMY_DIR_PATH);
}

