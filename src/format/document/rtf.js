import {Format} from "../../Format.js";

export class rtf extends Format
{
	name           = "Rich Text Format";
	website        = "http://fileformats.archiveteam.org/wiki/RTF";
	ext            = [".rtf"];
	forbidExtMatch = true;
	magic          = ["Rich Text Format"];
	converters     = ["fileMerlin", "soffice"];
}
