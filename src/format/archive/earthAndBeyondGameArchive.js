import {Format} from "../../Format.js";

export class earthAndBeyondGameArchive extends Format
{
	name           = "Earth and Beyond Game Archive";
	ext            = [".mix", ".pkg"];
	forbidExtMatch = true;
	magic          = ["Earth And Beyond game data archive", /^geArchive: MIX_MIX1( |$)/];
	converters     = ["gameextractor[codes:MIX_MIX1]"];
}
