import {Format} from "../../Format.js";

export class starOfficeDraw extends Format
{
	name           = "StarOffice Draw Document";
	website        = "http://fileformats.archiveteam.org/wiki/SDA_(StarOffice)";
	ext            = [".sda"];
	forbidExtMatch = true;
	magic          = ["StarOffice"];
	weakMagic      = true;
	converters     = ["soffice"];
}
