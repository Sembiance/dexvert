import {Format} from "../../Format.js";

export class nokiaStartupLogo extends Format
{
	name       = "Nokia Startup Logo";
	website    = "http://fileformats.archiveteam.org/wiki/Nokia_Startup_Logo";
	ext        = [".nsl"];
	magic      = ["Nokia Startup Logo Editor bitmap", "deark: nsl"];
	converters = ["deark[module:nsl]", "wuimg[matchType:magic]"];
}
