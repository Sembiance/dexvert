import {Format} from "../../Format.js";

export class sea extends Format
{
	name       = "Self Extracting Stuffit Archive";
	website    = "http://fileformats.archiveteam.org/wiki/SIT";
	ext        = [".sea"];
	magic      = ["Macintosh Application (MacBinary)", "Preferred Executable Format"];
	weakMagic  = true;
	converters = ["unar"];
}
