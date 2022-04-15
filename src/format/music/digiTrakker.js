import {xu} from "xu";
import {Format} from "../../Format.js";

export class digiTrakker extends Format
{
	name         = "DigiTrakker Module";
	website      = "http://fileformats.archiveteam.org/wiki/Digitrakker_module";
	ext          = [".mdl"];
	magic        = ["DigiTrakker MDL Module", "Digitrakker module"];
	metaProvider = ["musicInfo"];
	converters   = ["xmp", "zxtune123", "openmpt123"];

	// Ensure the result is at least 1 second long, otherwise it likely didn't work and it should move to the next converter
	verify = ({meta}) => meta.duration>=(xu.SECOND*2);
}
