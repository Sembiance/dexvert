import {Format} from "../../Format.js";

export class janesLongbow2GameArchive extends Format
{
	name           = "Jane's Longbow 2 Game Archive";
	ext            = [".tre"];
	forbidExtMatch = true;
	magic          = ["Jane's Longbow 2 game data archive", /^geArchive: TRE_SKNKTREE010A( |$)/];
	converters     = ["gameextractor[codes:TRE_SKNKTREE010A]"];
}
