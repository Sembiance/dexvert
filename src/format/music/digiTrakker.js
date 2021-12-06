import {Format} from "../../Format.js";

export class digiTrakker extends Format
{
	name         = "DigiTrakker Module";
	website      = "http://fileformats.archiveteam.org/wiki/Digitrakker_module";
	ext          = [".mdl"];
	magic        = ["DigiTrakker MDL Module", "Digitrakker module"];
	metaProvider = ["musicInfo"];
	converters   = ["xmp", "zxtune123", "openmpt123"];
}
