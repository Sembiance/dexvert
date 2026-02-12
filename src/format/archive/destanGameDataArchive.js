import {Format} from "../../Format.js";

export class destanGameDataArchive extends Format
{
	name           = "Destan game data archive";
	ext            = [".3dn"];
	forbidExtMatch = true;
	magic          = ["Destan game data archive", /^geArchive: 3DN_DESTAN( |$)/];
	converters     = ["gameextractor[codes:3DN_DESTAN]"];
}
