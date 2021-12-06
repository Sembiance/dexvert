import {Format} from "../../Format.js";

export class jamCracker extends Format
{
	name         = "JamCracker Module";
	website      = "http://fileformats.archiveteam.org/wiki/JAMCracker_Pro";
	ext          = [".jc"];
	magic        = [/^JamCracker [Mm]odule/];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
