import {Format} from "../../Format.js";

export class windowsProgramInfo extends Format
{
	name       = "Microsoft Windows Program Information File";
	website    = "http://fileformats.archiveteam.org/wiki/Program_information_file";
	ext        = [".pif"];
	magic      = ["Program Information File (Windows)", "Windows Program Information File", "Format: Microsoft Program Information", "Windows PIF Datei", "deark: pif"];
	converters = ["deark[module:pif]", "strings[matchType:magic][hasExtMatch]"];
}
