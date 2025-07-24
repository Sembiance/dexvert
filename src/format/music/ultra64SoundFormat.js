import {Format} from "../../Format.js";

export class ultra64SoundFormat extends Format
{
	name           = "Ultra64 Sound Format";
	website        = "http://fileformats.archiveteam.org/wiki/USF";
	ext            = [".usf", ".miniusf", ".usflib"];
	forbidExtMatch = true;
	magic          = ["USF Ultra64 Sound Format rip"];
	metaProvider   = ["musicInfo"];
	converters     = ["zxtune123"];
}
