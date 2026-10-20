import {Format} from "../../Format.js";

export class lightOfAltairPAK extends Format
{
	name           = "Light of Altair PAK";
	ext            = [".pak"];
	forbidExtMatch = true;
	magic          = [/^geArchive: PAK_PACKFILE( |$)/];
	converters     = ["gameextractor[codes:PAK_PACKFILE]"];
}
