import {Format} from "../../Format.js";

export class fontographer extends Format
{
	name       = "Fontographer";
	website    = "http://fileformats.archiveteam.org/wiki/Fontographer";
	ext        = [".fog"];
	magic      = ["Fontographer Font"];
	converters = ["fontographer"];
}
