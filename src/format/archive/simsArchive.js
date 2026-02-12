import {Format} from "../../Format.js";

export class simsArchive extends Format
{
	name           = "The Sims Archive";
	ext            = [".far"];
	forbidExtMatch = true;
	magic          = ["The Sims Archive", /^geArchive: FAR_FAR( |$)/];
	website        = "http://fileformats.archiveteam.org/wiki/FAR_(The_Sims)";
	converters     = ["gameextractor[codes:FAR_FAR]"];
}
