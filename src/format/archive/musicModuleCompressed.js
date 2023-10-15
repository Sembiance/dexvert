import {Format} from "../../Format.js";

export class musicModuleCompressed extends Format
{
	name       = "Music Module Compressed";
	magic      = ["MMCMP: Music Module Compressor"];
	packed     = true;
	converters = ["ancient"];
}
