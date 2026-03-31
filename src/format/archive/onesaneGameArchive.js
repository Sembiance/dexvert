import {Format} from "../../Format.js";

export class onesaneGameArchive extends Format
{
	name           = "1nsane game data archive";
	ext            = [".idf"];
	forbidExtMatch = true;
	magic          = ["1nsane game data archive"];
	converters     = ["vibeExtract"];
}
