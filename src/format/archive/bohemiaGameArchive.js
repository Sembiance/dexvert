import {Format} from "../../Format.js";

export class bohemiaGameArchive extends Format
{
	name           = "Bohemia game archive";
	ext            = [".pbo"];
	forbidExtMatch = true;
	magic          = ["Packed Bohemia Object game data archive", /^geArchive: PBO_SREV( |$)/];
	weakMagic      = true;
	converters     = ["gameextractor[codes:PBO_SREV]"];
}
