import {Format} from "../../Format.js";

export class soundFX extends Format
{
	name         = "SoundFX Module";
	website      = "http://fileformats.archiveteam.org/wiki/SoundFX_module";
	ext          = [".sfx", ".sfx2"];
	matchPreExt  = true;
	magic        = [/^SoundFX [Mm]odule/, "SoundFX 2 module"];
	metaProvider = ["musicInfo"];
	converters   = ["xmp", "uade123", "zxtune123", "openmpt123"];
}
