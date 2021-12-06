import {Format} from "../../Format.js";

export class asylum extends Format
{
	name         = "Asylum Module";
	ext          = [".amf"];
	magic        = ["Asylum Music Format module"];
	metaProvider = ["musicInfo"];
	converters   = ["xmp", "openmpt123"];
}
