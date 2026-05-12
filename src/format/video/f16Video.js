import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class f16Video extends Format
{
	name       = "F16 Video";
	ext        = [".f16"];
	idCheck    = async inputFile => inputFile.size>14 && (await fileUtil.readFileBytes(inputFile.absolute, 2, 12)).indexOfX([0x0F, 0x00])===0;
	converters = ["na_eofdec[format:f16]"];
	//unsupported = true; // No good way to identify them, other than extension, which would work, but the samples I tried with na_eofdec just produced black video with static sound, so pass on this format for now
}
