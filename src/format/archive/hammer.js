import {Format} from "../../Format.js";

export class hammer extends Format
{
	name       = "Hammer";
	website    = "http://fileformats.archiveteam.org/wiki/Hammer_(compression)";
	ext        = [".hmr"];
	magic      = ["Hammer compressed"];
	packed     = true;
	converters = ["hammer_decomp"];
}
