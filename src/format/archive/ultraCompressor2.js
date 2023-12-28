import {Format} from "../../Format.js";

export class ultraCompressor2 extends Format
{
	name       = "UltraCompressor II Archive";
	website    = "http://fileformats.archiveteam.org/wiki/UltraCompressor_II";
	ext        = [".uc2"];
	magic      = ["UC2 archive data", "UltraCompressor 2 Archive"];
	converters = ["ultraCompressor2"];
}
