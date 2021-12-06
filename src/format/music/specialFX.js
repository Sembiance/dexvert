import {Format} from "../../Format.js";

export class specialFX extends Format
{
	name         = "Special FX Module";
	website      = "http://fileformats.archiveteam.org/wiki/Special_FX";
	ext          = [".jd", ".doda"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
