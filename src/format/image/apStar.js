import {Format} from "../../Format.js";

export class apStar extends Format
{
	name       = "Atari AP* Image";
	website    = "http://fileformats.archiveteam.org/wiki/AP*";
	ext        = [".256", ".ap2", ".apa", ".apc", ".plm", ".mic"];
	fileSize   = [7720, 7680, 7684];
	converters = ["recoil2png[format:MIC,PLM,APC,AP2,256.256,APA]"];
}
