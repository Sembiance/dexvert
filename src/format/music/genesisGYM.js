import {Format} from "../../Format.js";

export class genesisGYM extends Format
{
	name         = "Genesis GYM";
	website      = "http://fileformats.archiveteam.org/wiki/GYM";
	ext          = [".gym"];
	magic        = ["Sega Genesis/Mega Drive sound/music data"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];
}
