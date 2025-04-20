import {Format} from "../../Format.js";

export class texFont extends Format
{
	name       = "TexFont Texture Mapped Font";
	website    = "http://fileformats.archiveteam.org/wiki/TexFont";
	ext        = [".txf"];
	magic      = ["TexFont"];
	converters = ["wuimg"];
}
