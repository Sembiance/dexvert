import {Format} from "../../Format.js";

export class leggless extends Format
{
	name         = "Leggless Music Editor Module";
	website      = "http://fileformats.archiveteam.org/wiki/Leggless_Music_Editor";
	ext          = [".lme"];
	magic        = ["Leggless Music Editor module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
