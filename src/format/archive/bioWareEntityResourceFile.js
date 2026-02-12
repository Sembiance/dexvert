import {Format} from "../../Format.js";

export class bioWareEntityResourceFile extends Format
{
	name           = "BioWare Entity Resource File";
	ext            = [".erf"];
	forbidExtMatch = true;
	magic          = ["BioWare Entity Resource File", /^geArchive: ERF_ERFV\d\d/];
	converters     = ["gameextractor[codes:ERF_ERFV10,ERF_ERFV20,ERF_ERFV30]"];
}
