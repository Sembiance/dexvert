import {Format} from "../../Format.js";

export class lionheadStudiosGameArchive extends Format
{
	name           = "Lionhead Studios game archive";
	ext            = [".sad"];
	forbidExtMatch = true;
	magic          = ["Generic Lionhead Studios game data", /^geArchive: SAD_LIONHEAD( |$)/];
	converters     = ["gameextractor[codes:SAD_LIONHEAD]"];
}
