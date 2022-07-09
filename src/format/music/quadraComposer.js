import {Format} from "../../Format.js";

export class quadraComposer extends Format
{
	name         = "Quadra Composer";
	website      = "http://fileformats.archiveteam.org/wiki/Quadra_Composer_module";
	ext          = [".emod"];
	magic        = ["Quadra Composer module"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123", "uade123"];
}
