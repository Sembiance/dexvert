import {Format} from "../../Format.js";

export class maud extends Format
{
	name         = "MacroSystem Audio";
	website      = "http://fileformats.archiveteam.org/wiki/IFF-MAUD";
	ext          = [".maud"];
	magic        = ["IFF data, MAUD MacroSystem audio", "IFF MacroSystem Audio", /^soxi: maud$/];
	metaProvider = ["soxi"];
	converters   = ["sox[type:maud]", "awaveStudio"];
}
