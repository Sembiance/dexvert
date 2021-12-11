import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class fmTownsOSApp extends Format
{
	name        = "FM-TownsOS App";
	ext         = [".exp"];
	magic       = ["FM-TownsOS EXP"];
	weakMagic   = true;
	unsupported = true;

	// We have to do this instead of byteCheck because we have two possible different headers to check and byteCheck doesn't currently support that
	idCheck = async inputFile =>
	{
		const arr = await fileUtil.readFileBytes(inputFile.absolute, 2);
		return [[0x50, 0x33], [0x4D, 0x50]].some(v => arr.indexOfX(v)===0);
	};
}
