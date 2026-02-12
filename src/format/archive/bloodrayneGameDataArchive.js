import {Format} from "../../Format.js";

export class bloodrayneGameDataArchive extends Format
{
	name           = "Bloodrayne game data archive";
	ext            = [".pod"];
	forbidExtMatch = true;
	magic          = ["Bloodrayne game data archive", /^geArchive: POD_POD3( |$)/];
	weakMagic      = ["Bloodrayne game data archive"];
	converters     = ["gameextractor[codes:POD_POD3]"];
}
