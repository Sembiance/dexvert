import {Format} from "../../Format.js";

export class jamCracker extends Format
{
	name         = "JamCracker Module";
	website      = "http://fileformats.archiveteam.org/wiki/JAMCracker_Pro_module";
	ext          = [".jc"];
	magic        = [/^JamCracker [Mm]odule/, /^fmt\/975( |$)/];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
