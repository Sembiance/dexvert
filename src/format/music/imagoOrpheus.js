import {Format} from "../../Format.js";

export class imagoOrpheus extends Format
{
	name         = "Imago Orpheus Module";
	website      = "http://fileformats.archiveteam.org/wiki/Imago_Orpheus_module";
	ext          = [".imf"];
	magic        = ["Imago Orpheus module"];
	metaProvider = ["musicInfo"];
	converters   = ["xmp", "zxtune123", "openmpt123"];
}
