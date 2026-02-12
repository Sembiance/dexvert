import {Format} from "../../Format.js";

export class gabrielKnight3BarnGameArchive extends Format
{
	name           = "Gabriel Knight 3 barn game archive";
	ext            = [".brn"];
	forbidExtMatch = true;
	magic          = ["Gabriel Knight 3 barn game data", /^geArchive: BRN_GK3BARN( |$)/];
	converters     = ["gameextractor[codes:BRN_GK3BARN]"];
}
