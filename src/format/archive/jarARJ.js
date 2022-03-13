import {Format} from "../../Format.js";

export class jarARJ extends Format
{
	name       = "JAR Archive (ARJ Software)";
	website    = "http://fileformats.archiveteam.org/wiki/JAR_(ARJ_Software)";
	ext        = [".j"];
	magic      = ["JAR (ARJ Software, Inc.) archive data", /^JAR [Cc]ompressed [Aa]rchive/];
	converters = ["jar32"];
}
