import {Format} from "../../Format.js";

export class nokiaStartupLogo extends Format
{
	name       = "Nokia Startup Logo";
	website    = "http://fileformats.archiveteam.org/wiki/Nokia_Startup_Logo";
	ext        = [".nsl"];
	magic      = ["Nokia Startup Logo Editor bitmap"];
	converters = ["deark[module:nsl]", "nconvert"];
}
