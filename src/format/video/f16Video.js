import {Format} from "../../Format.js";

export class f16Video extends Format
{
	name       = "F16 Video";
	ext        = [".f16"];
	byteCheck  = [{offset : 12, match : [0x0F, 0x00]}];
	converters = ["na_eofdec[format:f16]"];
}
