import {Format} from "../../Format.js";

export class f16Video extends Format
{
	name       = "F16 Video";
	ext        = [".f16"];
	byteCheck  = [{offset : 12, match : [0x0F, 0x00]}];
	converters = ["na_eofdec[format:f16]"];
	//unsupported = true; // No good way to identify them, other than extension, which would work, but the samples I tried with na_eofdec just produced black video with static sound, so pass on this format for now
}
