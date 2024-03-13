import {Format} from "../../Format.js";

export class asylum extends Format
{
	name         = "Asylum Module";
	website      = "http://fileformats.archiveteam.org/wiki/Asylum_Music_Format";
	ext          = [".amf"];
	magic        = ["Asylum Music Format module", /^fmt\/1622( |$)/];
	metaProvider = ["musicInfo"];
	converters   = ["xmp", "openmpt123"];
}
