import {Format} from "../../Format.js";

export class ripScrip extends Format
{
	name       = "Remote Imaging Protocol Script";
	website    = "http://fileformats.archiveteam.org/wiki/RIPscrip";
	ext        = [".rip"];
	magic      = ["RIPscript", "ANSI escape sequence text"];
	weakMagic  = ["ANSI escape sequence text"];
	converters = ["pabloDrawConsole"];
}
