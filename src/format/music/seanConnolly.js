import {Format} from "../../Format.js";

export class seanConnolly extends Format
{
	name         = "Sean Connolly Module";
	website      = "http://fileformats.archiveteam.org/wiki/Sean_Connolly";
	ext          = [".scn"];
	magic        = ["Sean Connolly module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
