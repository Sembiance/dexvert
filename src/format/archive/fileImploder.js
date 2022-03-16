import {Format} from "../../Format.js";

export class fileImploder extends Format
{
	name       = "File Imploder";
	website    = "http://fileformats.archiveteam.org/wiki/File_Imploder";
	ext        = [".imp"];
	magic      = ["File Imploder compressed data", "IMP: File Imploder"];
	converters = ["ancient"];
}
