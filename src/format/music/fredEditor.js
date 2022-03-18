import {Format} from "../../Format.js";

export class fredEditor extends Format
{
	name         = "Fred Editor Module";
	website      = "http://fileformats.archiveteam.org/wiki/Fred_Editor";
	ext          = [".fred", ".frd"];
	magic        = ["Fred Editor module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123[player:Fred]"];
}
