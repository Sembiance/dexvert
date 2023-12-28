import {Format} from "../../Format.js";

export class artAndMagic extends Format
{
	name         = "Art & Magic Module";
	website      = "http://fileformats.archiveteam.org/wiki/Art_&_Magic";
	ext          = [".aam"];
	magic        = ["Art And Magic module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
