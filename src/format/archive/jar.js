import {Format} from "../../Format.js";

export class jar extends Format
{
	name       = "JAR Archive";
	website    = "http://fileformats.archiveteam.org/wiki/Jar";
	ext        = [".jar", ".j"];
	magic      = ["Java archive data"];
	converters = ["unzip", "sevenZip", "unar"];
}
