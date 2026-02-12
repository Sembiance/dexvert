import {Format} from "../../Format.js";

export class digitalIllusionsGameArchive extends Format
{
	name           = "Digital Illusions game archive";
	ext            = [".pdo", ".rmpublisher", ".rmlanguage", ".pdt", ".dta"];
	forbidExtMatch = true;
	magic          = ["Digital Illusions game data package", /^geArchive: PDT_PDI1( |$)/];
	weakMagic      = true;
	converters     = ["gameextractor[codes:PDT_PDI1]"];
}
