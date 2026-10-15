import {Format} from "../../Format.js";

export class rncArchive extends Format
{
	name           = "Pro-Pack RNC Archive";
	website        = "http://fileformats.archiveteam.org/wiki/Pro-Pack";
	ext            = [".rnc"];
	forbidExtMatch = true;
	magic          = ["RNC / PRO-PACK archive", "RNC Archiv gefunden"];
	packed         = true;
	converters     = ["proPack", "proPack[flat]"];
}
