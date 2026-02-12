import {Format} from "../../Format.js";

export class madsHAGGameArchive extends Format
{
	name           = "MADS HAG Game Archive";
	ext            = [".hag"];
	forbidExtMatch = true;
	magic          = ["MADS HAG game data archive", /^geArchive: HAG_MADSCONCAT1( |$)/];
	converters     = ["gameextractor[codes:HAG_MADSCONCAT1]"];
}
