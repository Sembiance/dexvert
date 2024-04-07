import {Format} from "../../Format.js";

export class sea extends Format
{
	name       = "Self Extracting Stuffit Archive";
	website    = "http://fileformats.archiveteam.org/wiki/StuffIt";
	ext        = [".sea"];
	magic      = ["Macintosh Application (MacBinary)", "Preferred Executable Format"];
	weakMagic  = true;
	idMeta     = ({macFileType, macFileCreator}) => macFileType==="APPL" && macFileCreator==="EXTR";
	converters = ["unar[mac]"];
}
