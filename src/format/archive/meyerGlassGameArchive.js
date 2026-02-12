import {Format} from "../../Format.js";

export class meyerGlassGameArchive extends Format
{
	name           = "Meyer/Glass Interactive Game Archive";
	ext            = [".mgf"];
	forbidExtMatch = true;
	magic          = ["Meyer/Glass Interactive game data Format", /^geArchive: MGF_MGFS( |$)/];
	converters     = ["gameextractor[codes:MGF_MGFS]"];
}
