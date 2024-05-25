import {Format} from "../../Format.js";

export class peaZip extends Format
{
	name       = "PeaZip Archive";
	website    = "http://fileformats.archiveteam.org/wiki/PEA";
	ext        = [".pea"];
	magic      = ["PEA compressed archive", "Archive: PeaZip Archive", /^fmt\/1095( |$)/];
	converters = ["peazip"];
}
