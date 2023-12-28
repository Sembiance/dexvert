import {xu} from "xu";
import {fileUtil} from "xutil";
import {path} from "std";
import {formats, init as initFormats} from "../../src/format/formats.js";

const SAMPLES_DIR_PATH = path.join(xu.dirname(import.meta), "..", "..", "test", "sample");
export default async function buildUNSUPPORTED(xlog)
{
	await initFormats(xlog);
	
	const unsupportedFormats = Object.fromEntries(Object.entries(formats).filter(([, format]) => format.unsupported));

	xlog.info`Writing UNSUPPORTED.md to disk...`;
	await fileUtil.writeTextFile(path.join(xu.dirname(import.meta), "..", "..", "UNSUPPORTED.md"), `# Unsupported File Formats (${Object.keys(unsupportedFormats).length.toLocaleString()})
These formats can still be **identified** by dexvert, they just are not converted into modern ones.<br>
Some are not converted because they are not very useful, or are specific to a single application.<br>
Others are not converted because it was deemed low priority, or there are no known programs to do so.

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
				noteParts.push(`[${formatSamples.length.toLocaleString()} sample file${formatSamples.length===1 ? "" : "s"}](https://sembiance.com/fileFormatSamples/${path.relative(SAMPLES_DIR_PATH, formatSampleDirPath)}/)`);
			}
			
			const noteText = (f.notes || "").replaceAll("\n", " ").trim();
			if(noteText && noteText.length>0)
				noteParts.push(noteText);
			return (`${f.familyid} | ${f.website ? `[${f.name}](${f.website})` : f.name} | ${(f.ext || []).join(" ")} | ${noteParts.join(" - ")}`);
		})).join("\n")}
`)).join("\n")}
`);
}

