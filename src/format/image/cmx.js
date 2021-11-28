import {Format} from "../../Format.js";

export class cmx extends Format
{
	name           = "Corel Metafile Exchange Image";
	website        = "http://fileformats.archiveteam.org/wiki/CMX";
	ext            = [".cmx"];
	forbidExtMatch = true;
	magic          = ["Corel Metafile Exchange Image", "Corel Presentation Exchange File"];
	converters     = ["soffice[outType:svg]", "deark"];
}
