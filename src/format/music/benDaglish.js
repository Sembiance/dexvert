import {Format} from "../../Format.js";

export class benDaglish extends Format
{
	name         = "Ben Daglish";
	website      = "http://fileformats.archiveteam.org/wiki/Ben_Daglish";
	ext          = [".bd"];
	magic        = [/^Ben Daglish$/];
	metaProvider = ["musicInfo"];
	converters   = ["uade123[player:BenDaglish]"];
}
