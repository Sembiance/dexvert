import {Format} from "../../Format.js";

export class seanConran extends Format
{
	name         = "Sean Conran Module";
	website      = "http://fileformats.archiveteam.org/wiki/Sean_Conran";
	ext          = [".scr"];
	magic        = ["Sean Conran module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
