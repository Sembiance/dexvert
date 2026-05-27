import {Format} from "../../Format.js";

export class afterlifeGameData extends Format
{
	name           = "Afterlife game data";
	ext            = [".000"];
	forbidExtMatch = true;
	magic          = ["Afterlife game data", /^geArchive: 000_FFIJ( |$)/];
	byteCheck      = [{offset : 0, match : [0x46, 0x46, 0x49, 0x4A]}];	// FFIJ
	converters     = ["gameextractor[codes:000_FFIJ]"];
}
