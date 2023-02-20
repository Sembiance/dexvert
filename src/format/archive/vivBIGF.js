import {Format} from "../../Format.js";

export class vivBIGF extends Format
{
	name       = "VIV BIGF";
	website    = "http://fileformats.archiveteam.org/wiki/VIV";
	ext        = [".viv", ".big"];
	magic      = ["VIV/BIGF Electronic Arts Game Archive"];
	weakMagic  = true;
	converters = ["gameextractor"];
}
