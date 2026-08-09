import {Format} from "../../Format.js";

export class composer667 extends Format
{
	name         = "Composer 667 Module";
	website      = "http://fileformats.archiveteam.org/wiki/Composer_667";
	ext          = [".667"];
	magic        = ["Composer 667 module"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123", "openmpt123"];
}
