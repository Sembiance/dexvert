import {Format} from "../../Format.js";

export class openDocument extends Format
{
	name           = "Open Document Format for Office Applications";
	website        = "http://fileformats.archiveteam.org/wiki/OpenDocument";
	ext            = [".odm", ".odt", ".fodt", ".ott"];
	forbidExtMatch = true;
	magic          = ["OpenDocument Text", "OpenDocument Master Text document", "OpenDocument Master Document"];
	converters     = ["soffice"];
}
