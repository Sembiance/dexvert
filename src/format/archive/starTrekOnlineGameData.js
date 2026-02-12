import {Format} from "../../Format.js";

export class starTrekOnlineGameData extends Format
{
	name           = "Star Trek Online game data";
	ext            = [".hogg"];
	forbidExtMatch = true;
	magic          = ["Star Trek Online game data", /^geArchive: HOGG( |$)/];
	converters     = ["gameextractor[codes:HOGG]"];
}
