import {Format} from "../../Format.js";

export class epicMegagamesMASI extends Format
{
	name         = "Epic Megagames MASI Module";
	website      = "http://fileformats.archiveteam.org/wiki/Epic_Megagames_MASI";
	ext          = [".psm"];
	magic        = ["Epic Megagames MASI module"];
	metaProvider = ["musicInfo"];
	converters   = ["xmp", "zxtune123", "openmpt123"];
}
