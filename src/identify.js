import {xu} from "xu";
import {Format} from "./Format.js";
import {Program} from "./Program.js";
import {FileSet} from "./FileSet.js";

export async function identify(inputFilePath, {verbose})
{
	const input = await FileSet.create(inputFilePath);
	const detections = (await Promise.all(["file", "trid", "checkBytes", "dexmagic"].map(programid => Program.runProgram(programid, input, undefined, {verbose})))).flatMap(o => o.meta.detections);

	if(verbose)
		console.log("raw detections:\n", detections.map(({confidence, from, value, extensions}) => ({"%" : confidence, from, value, extensions})));

	//console.log(detections);
	// TODO: Add dexmagic (convert custom file_magic)

	// TODO: Now add aux files to input and check Match.checkFormat() for each format
	//const formats = await Format.loadFormats();
}
