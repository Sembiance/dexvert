import {Format} from "../../Format.js";

export class harryPotterQuidditchWorldCupArchive extends Format
{
	name           = "Harry Potter: Quidditch World Cup archive";
	ext            = [".ccd"];
	forbidExtMatch = true;
	magic          = ["Harry Potter: Quidditch World Cup game data archive", /^geArchive: CCD_FKNL( |$)/];
	converters     = ["gameextractor[codes:CCD_FKNL]"];
}
