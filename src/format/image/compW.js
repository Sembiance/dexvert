import {Format} from "../../Format.js";

export class compW extends Format
{
	name       = "CompW";
	website    = "http://fileformats.archiveteam.org/wiki/WLM";
	ext        = [".wlm"];
	magic      = ["CompW bitmap"];
	converters = ["nconvertWine"];
}
