import {xu} from "xu";
import {fileUtil} from "xutil";
import {path} from "std";
import {formats} from "../../src/format/formats.js";

const unsupportedFormats = Object.fromEntries(Object.entries(formats).filter(([, format]) => format.unsupported));
const SAMPLES_DIR_PATH = path.join(xu.dirname(import.meta), "..", "..", "test", "sample");
export default async function buildUNSUPPORTED()
{
	xu.log3`Writing UNSUPPORTED.md to disk...`;
	await fileUtil.writeFile(path.join(xu.dirname(import.meta), "..", "..", "UNSUPPORTED.md"), `# **${Object.keys(unsupportedFormats).length.toLocaleString()}** Unsupported File Formats
These formats can still be **identified** by dexvert, just can't be converted into modern ones.

${(await Object.values(unsupportedFormats).map(f => f.familyid).unique().sortMulti().parallelMap(async familyid => `

## ${familyid.toProperCase()} (${Object.values(unsupportedFormats).filter(f => f.familyid===familyid).length.toLocaleString()})
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
${(await Object.values(unsupportedFormats).filter(f => f.familyid===familyid).sortMulti(f => f.name).parallelMap(async f =>
		{
			const noteParts = [];
			let formatSampleDirPath = path.join(SAMPLES_DIR_PATH, `${f.familyid}/${f.formatid}`);
			if(!await fileUtil.exists(formatSampleDirPath))
				formatSampleDirPath = path.join(SAMPLES_DIR_PATH, `unsupported/${f.formatid}`);
			if(await fileUtil.exists(formatSampleDirPath))
			{
				const formatSamples = await fileUtil.tree(formatSampleDirPath);
				noteParts.push(`[${formatSamples.length.toLocaleString()} sample file${formatSamples.length===1 ? "" : "s"}](https://telparia.com/fileFormatSamples/${path.relative(SAMPLES_DIR_PATH, formatSampleDirPath)}/)`);
			}
			
			const noteText = (f.notes || "").replaceAll("\n", " ").trim();
			if(noteText && noteText.length>0)
				noteParts.push(noteText);
			return (`${f.familyid} | ${f.website ? `[${f.name}](${f.website})` : f.name} | ${(f.ext || []).join(" ")} | ${noteParts.join(" - ")}`);
		})).join("\n")}
`)).join("\n")}
`);
}

