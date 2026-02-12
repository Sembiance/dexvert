import {Format} from "../../Format.js";

export class redengineGameArchive extends Format
{
	name           = "REDengine game Archive";
	ext            = [".rda"];
	forbidExtMatch = true;
	magic          = ["REDengine game data Archive", /^geArchive: RDA( |$)/];
	converters     = ["gameextractor[codes:RDA]"];
}
