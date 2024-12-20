import {Format} from "../../Format.js";

export class spc extends Format
{
	name         = "SPC";
	website      = "http://fileformats.archiveteam.org/wiki/SPC_(Audio)";
	ext          = [".spc"];
	magic        = ["SNES SPC700 sound file", "Super Famicon/Super NES audio dump"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];
}
