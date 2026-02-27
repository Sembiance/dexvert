import {Format} from "../../Format.js";

export class nibiruGRP extends Format
{
	name           = "Nibiru GRP Archive";
	ext            = [".grp"];
	forbidExtMatch = true;
	magic          = [/^geArchive: GRP( |$)/];
	converters     = ["gameextractor[codes:GRP]"];
}
