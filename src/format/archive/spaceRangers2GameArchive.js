import {Format} from "../../Format.js";

export class spaceRangers2GameArchive extends Format
{
	name           = "Space Rangers 2 Game Archive";
	ext            = [".pkg"];
	forbidExtMatch = true;
	magic          = [/^geArchive: PKG( |$)/];
	converters     = ["gameextractor[codes:PKG]"];
}
