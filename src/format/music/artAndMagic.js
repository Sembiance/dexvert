import {Format} from "../../Format.js";

export class artAndMagic extends Format
{
	name         = "Art & Magic Module";
	website      = "http://fileformats.archiveteam.org/wiki/Art_%26_Magic";
	ext          = [".aam"];
	magic        = ["Art And Magic module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
