import {Format} from "../../Format.js";

export class jar extends Format
{
	name       = "JAR Archive";
	website    = "http://fileformats.archiveteam.org/wiki/Jar";
	ext        = [".jar", ".j"];
	magic      = ["Java archive data", "Java Archive", "Java Enterprise Archive", /^x-fmt\/412( |$)/];
	converters = ["unzip", "sevenZip", "unar"];
}
