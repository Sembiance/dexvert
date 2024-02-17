import {Format} from "../../Format.js";

export class sonicArranger extends Format
{
	name         = "Sonic Arrange Module";
	website      = "http://fileformats.archiveteam.org/wiki/Sonic_Arranger";
	ext          = [".sa"];
	magic        = ["Sonic Arranger module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
