import {Format} from "../../Format.js";

export class chiefLZ extends Format
{
	name           = "ChiefLZ LZA Compressed";
	website        = "http://fileformats.archiveteam.org/wiki/ChiefLZ";
	ext            = ["_"];
	forbidExtMatch = true;
	packed         = true;
	magic          = ["LZA compressed data"];
	converters     = ["lza"];
}
