import {Format} from "../../Format.js";

export class mo3 extends Format
{
	name         = "MO3 Module";
	website      = "https://wiki.multimedia.cx/index.php/MO3";
	ext          = [".mo3"];
	magic        = ["MO3 module", "MOdule with MP3 Version", "audio/x-mo3"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123", "openmpt123"];
}
