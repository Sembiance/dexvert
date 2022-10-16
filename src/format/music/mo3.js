import {Format} from "../../Format.js";

export class mo3 extends Format
{
	name         = "MO3 Module";
	website      = "http://www.un4seen.com/mo3.html";
	ext          = [".mo3"];
	magic        = ["MO3 module", "MOdule with MP3 Version"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123", "openmpt123"];
}
