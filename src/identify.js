import {xu} from "xu";
import {Format} from "./Format.js";
import {Program} from "./Program.js";
import {FileSet} from "./FileSet.js";

export async function identify(inputFilePath, {verbose=0})
{
	const input = await FileSet.create(inputFilePath);
	const [fileState, tridState] = await Promise.all([Program.runProgram("file", input), Program.runProgram("trid", input)]);
	// TODO: Add dexmagic (convert custom file_magic)

	// TODO: Now add aux files to input and check Match.checkFormat() for each format
	//const formats = await Format.loadFormats();
	console.log(fileState.meta.matches, tridState.meta.matches);
}
