import {Format} from "../../Format.js";

export class generalDigiMusic extends Format
{
	name         = "General Digital Music";
	website      = "http://fileformats.archiveteam.org/wiki/General_Digital_Music_module";
	ext          = [".gdm"];
	magic        = ["General Digital Music"];
	metaProvider = ["musicInfo"];
	converters   = ["xmp", "zxtune123", "openmpt123"];
}
