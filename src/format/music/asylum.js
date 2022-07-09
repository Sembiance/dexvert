import {Format} from "../../Format.js";

export class asylum extends Format
{
	name         = "Asylum Module";
	website      = "http://fileformats.archiveteam.org/wiki/Asylum_Music_Format";
	ext          = [".amf"];
	magic        = ["Asylum Music Format module"];
	metaProvider = ["musicInfo"];
	converters   = ["xmp", "openmpt123"];
}
