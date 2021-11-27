import {Format} from "../../Format.js";

export class kssPaint extends Format
{
	name       = "KSS-Paint";
	website    = "http://fileformats.archiveteam.org/wiki/KSS-Paint";
	ext        = [".kss"];
	converters = ["recoil2png"]
}
