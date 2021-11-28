import {Format} from "../../Format.js";

export class fbi extends Format
{
	name       = "FLIP Image";
	website    = "http://fileformats.archiveteam.org/wiki/FLIP";
	ext        = [".fbi"];
	magic      = ["SysEx File"];
	weakMagic  = true;
	converters = ["recoil2png"];
}
