import {Format} from "../../Format.js";

export class kssMusic extends Format
{
	name         = "KSS Music File";
	website      = "http://fileformats.archiveteam.org/wiki/KSS";
	ext          = [".kss"];
	magic        = ["KSS music file", /^KSSX? music format dump$/];
	notes        = "Not all files convert correctly, such as prologue.kss and circus charlie.kss. Other software listed at website link, could try those to convert";
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];
}
