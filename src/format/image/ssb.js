import {Format} from "../../Format.js";

export class ssb extends Format
{
	name       = "Sinbad Slideshow";
	website    = "http://fileformats.archiveteam.org/wiki/Sinbad_Slideshow";
	ext        = [".ssb"];
	fileSize   = 32768;
	converters = ["recoil2png"];
}
