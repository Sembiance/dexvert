import {Format} from "../../Format.js";

export class composer669 extends Format
{
	name         = "Composer 669 Module";
	website      = "http://fileformats.archiveteam.org/wiki/669";
	ext          = [".669"];
	magic        = ["Composer 669 module", "Unis 669 module"];
	metaProvider = ["musicInfo"];
	converters   = ["xmp", "zxtune123", "openmpt123"];
}
