import {xu} from "xu";
import {Format} from "../../Format.js";

export class cpi extends Format
{
	name       = "Macro Pixel Editor";
	website    = "http://fileformats.archiveteam.org/wiki/Marco_Pixel_Editor";
	ext        = [".cpi"];
	idCheck    = inputFile => inputFile.size<=(xu.KB*10);	// Due to no magic, just extension, restrict to only matching files <10K as the largest sample I have is 6947 bytes
	converters = ["recoil2png[format:CPI]"];
}
